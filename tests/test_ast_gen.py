import unittest
import difflib
from textwrap import dedent

import support

import py2c._ast_gen as ast_gen
from py2c._ast_gen import Node, Attr


class ParserTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for Parsing of structures"""

    def setUp(self):
        self.parser = ast_gen.Parser()

    def template(self, test_string, expected):
        self.parser.prepare(str(test_string))
        self.assertEqual(self.parser.data, expected)

    def assertMultiLineEqual(self, first, second, msg=None):
        """Assert that two multi-line strings are equal.

        If they aren't, show a nice diff.
        """
        self.assertTrue(isinstance(first, str), 'Argument 1 is not a string')
        self.assertTrue(isinstance(second, str), 'Argument 2 is not a string')

        if first != second:
            message = ''.join(difflib.ndiff(first.splitlines(True),
                                            second.splitlines(True)))
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)


class CommentTestCase(ParserTestCase):
    """Tests for Parser parsing comments"""
    # Overridden!
    def template(self, text, expected=None, msg=None):
        if expected is None:
            expected = text
        self.assertEqual(self.parser.remove_comments(text), expected, msg)

    def test_comment_empty_line(self):
        "Checks if Parser handles empty lines with comments correctly"
        self.template(
            "#test: [a,string]",
            ""
        )

    def test_comment_no_arg(self):
        "Checks if Parser handles Nodes with comments correctly"
        self.template(
            "foo: [] #test: [a,string]",
            "foo: [] "
        )

    def test_comment_newline(self):
        "Checks if Parser handles multiple lines with comments correctly"
        self.template(
            "foo # test\nblah",
            "foo \nblah"
        )


class PropertyTestCase(ParserTestCase):
    """Tests for Parser's parsing of Properties"""

    def test_property_empty(self):
        self.template(
            "foo: []",
            [Node('foo', [])]
        )

    def test_property_1arg(self):
        self.template(
            "foo: [bar]",
            [Node('foo', [Attr('bar', None, False)])]
        )

    def test_property_multi_arg(self):
        self.template(
            "foo: [bar, baz]",
            [Node('foo', [
                Attr('bar', None, False), Attr('baz', None, False)])]
        )

    def test_property_1arg_default(self):
        self.template(
            "foo: [bar=None]",
            [Node('foo', [Attr('bar', 'None', False)])]
        )

    def test_property_multi_arg_default(self):
        self.template(
            "foo: [bar, baz=None]",
            [Node('foo', [
                Attr('bar', None, False),
                Attr('baz', 'None', False)
            ])]
        )

    def test_default(self):
        "Tests for default values' conversion to sources"
        self.template(
            "foo: [a=True, b=False, c=None, d]",
            [Node('foo', [
                Attr('a', 'True', False),
                Attr('b', 'False', False),
                Attr('c', 'None', False),
                Attr('d', None, False),
            ])]
        )

    def test_invalid_object_to_prepare(self):
        errors = [TypeError, ast_gen.LexerError, ast_gen.ParsingError]
        args = [1,  "foo: [$x]", "foo: [x y]"]
        # Iterate over errors and arguments
        for err, arg in zip(errors, args):
            self.assertRaises(err, self.parser.prepare, arg)


class GenerationTestCase(ParserTestCase):
    """Tests for generated sources"""

    def check_output(self, text, expected_output):
        # Remove the prefix
        self.parser.prefix = ""
        # Give the parser the nodes text to prepare data for generating source
        self.parser.prepare(text)
        # Create a fake file
        fake = support.StringIO()
        # Generate the sources
        self.parser.write_module(fake)
        # Check output
        self.assertMultiLineEqual(
            fake.getvalue().strip(), dedent(expected_output).strip()
        )

    def test_output_single_nodefault(self):
        self.check_output(
            "FooBar: [bar]",
            """
            class FooBar(AST):
                def __init__(self, *args, **kwargs):
                    self._attrs = [('bar', None, False)]
                    super(FooBar, self).__init__(*args, **kwargs)
            """
        )

    def test_output_multiple_nodefault(self):
        self.check_output(
            "FooBar: [bar, baz]",
            """
            class FooBar(AST):
                def __init__(self, *args, **kwargs):
                    self._attrs = [
                        ('bar', None, False),
                        ('baz', None, False)
                    ]
                    super(FooBar, self).__init__(*args, **kwargs)
            """
        )

    def test_output_single_default(self):
        self.check_output(
            "FooBar: [bar=None]",
            """
            class FooBar(AST):
                def __init__(self, *args, **kwargs):
                    self._attrs = [('bar', 'None', False)]
                    super(FooBar, self).__init__(*args, **kwargs)
            """
        )

    def test_output_multiple_default(self):
        self.check_output(
            "FooBar: [foo=False, bar=True, baz]",
            """
            class FooBar(AST):
                def __init__(self, *args, **kwargs):
                    self._attrs = [
                        ('foo', 'False', False),
                        ('bar', 'True', False),
                        ('baz', None, False)
                    ]
                    super(FooBar, self).__init__(*args, **kwargs)
            """
        )


# As implemented for Issue 13857 in Python 3.3
# Replicated to stay compatible with earlier Python versions
class IndentTestCase(unittest.TestCase):
    # The examples used for tests. If any of these change, the expected
    # results in the various test cases must also be updated.
    # The round-trip cases are separate, because textwrap.dedent doesn't
    # handle Windows line endings
    ROUNDTRIP_CASES = (
        # Basic test case
        "Hi.\nThis is a test.\nTesting.",
        # Include a blank line
        "Hi.\nThis is a test.\n\nTesting.",
        # Include leading and trailing blank lines
        "\nHi.\nThis is a test.\nTesting.\n",
    )
    CASES = ROUNDTRIP_CASES + (
        # Use Windows line endings
        "Hi.\r\nThis is a test.\r\nTesting.\r\n",
        # Pathological case
        "\nHi.\r\nThis is a test.\n\r\nTesting.\r\n\n",
    )

    def test_indent_nomargin_default(self):
        # indent should do nothing if 'prefix' is empty.
        for text in self.CASES:
            self.assertEqual(ast_gen.indent(text, ''), text)

    def test_indent_nomargin_explicit_default(self):
        # The same as test_indent_nomargin, but explicitly requesting
        # the default behavior by passing None as the predicate
        for text in self.CASES:
            self.assertEqual(ast_gen.indent(text, '', None), text)

    def test_indent_nomargin_all_lines(self):
        # The same as test_indent_nomargin, but using the optional
        # predicate argument
        predicate = lambda line: True
        for text in self.CASES:
            self.assertEqual(ast_gen.indent(text, '', predicate), text)

    def test_indent_no_lines(self):
        # Explicitly skip indenting any lines
        predicate = lambda line: False
        for text in self.CASES:
            self.assertEqual(ast_gen.indent(text, '    ', predicate), text)

    def test_roundtrip_spaces(self):
        # A whitespace prefix should round-trip with dedent
        for text in self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(ast_gen.indent(text, '    ')), text)

    def test_roundtrip_tabs(self):
        # A whitespace prefix should round-trip with dedent
        for text in self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(ast_gen.indent(text, '\t\t')), text)

    def test_roundtrip_mixed(self):
        # A whitespace prefix should round-trip with dedent
        for text in self.ROUNDTRIP_CASES:
            self.assertEqual(dedent(ast_gen.indent(text, ' \t  \t ')), text)

    def test_indent_default(self):
        # Test default indenting of lines that are not whitespace only
        prefix = '  '
        expected = (
            # Basic test case
            "  Hi.\n  This is a test.\n  Testing.",
            # Include a blank line
            "  Hi.\n  This is a test.\n\n  Testing.",
            # Include leading and trailing blank lines
            "\n  Hi.\n  This is a test.\n  Testing.\n",
            # Use Windows line endings
            "  Hi.\r\n  This is a test.\r\n  Testing.\r\n",
            # Pathological case
            "\n  Hi.\r\n  This is a test.\n\r\n  Testing.\r\n\n",
        )
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(ast_gen.indent(text, prefix), expect)

    def test_indent_explicit_default(self):
        # Test default indenting of lines that are not whitespace only
        prefix = '  '
        expected = (
            # Basic test case
            "  Hi.\n  This is a test.\n  Testing.",
            # Include a blank line
            "  Hi.\n  This is a test.\n\n  Testing.",
            # Include leading and trailing blank lines
            "\n  Hi.\n  This is a test.\n  Testing.\n",
            # Use Windows line endings
            "  Hi.\r\n  This is a test.\r\n  Testing.\r\n",
            # Pathological case
            "\n  Hi.\r\n  This is a test.\n\r\n  Testing.\r\n\n",
        )
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(ast_gen.indent(text, prefix, None), expect)

    def test_indent_all_lines(self):
        # Add 'prefix' to all lines, including whitespace-only ones.
        prefix = '  '
        expected = (
            # Basic test case
            "  Hi.\n  This is a test.\n  Testing.",
            # Include a blank line
            "  Hi.\n  This is a test.\n  \n  Testing.",
            # Include leading and trailing blank lines
            "  \n  Hi.\n  This is a test.\n  Testing.\n",
            # Use Windows line endings
            "  Hi.\r\n  This is a test.\r\n  Testing.\r\n",
            # Pathological case
            "  \n  Hi.\r\n  This is a test.\n  \r\n  Testing.\r\n  \n",
        )
        predicate = lambda line: True
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(ast_gen.indent(text, prefix, predicate), expect)

    def test_indent_empty_lines(self):
        # Add 'prefix' solely to whitespace-only lines.
        prefix = '  '
        expected = (
            # Basic test case
            "Hi.\nThis is a test.\nTesting.",
            # Include a blank line
            "Hi.\nThis is a test.\n  \nTesting.",
            # Include leading and trailing blank lines
            "  \nHi.\nThis is a test.\nTesting.\n",
            # Use Windows line endings
            "Hi.\r\nThis is a test.\r\nTesting.\r\n",
            # Pathological case
            "  \nHi.\r\nThis is a test.\n  \r\nTesting.\r\n  \n",
        )
        predicate = lambda line: not line.strip()
        for text, expect in zip(self.CASES, expected):
            self.assertEqual(ast_gen.indent(text, prefix, predicate), expect)


if __name__ == '__main__':
    unittest.main(verbosity=1)
