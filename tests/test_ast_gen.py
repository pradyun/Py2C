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

    def test_single_nodefault(self):
        self.check_output(
            "FooBar: [bar]",
            """
            class FooBar(AST):
                _attrs = [('bar', None, False)]
            """
        )

    def test_multiple_nodefault(self):
        self.check_output(
            "FooBar: [bar, baz]",
            """
            class FooBar(AST):
                _attrs = [
                    ('bar', None, False),
                    ('baz', None, False)
                ]
            """
        )

    def test_single_default(self):
        self.check_output(
            "FooBar: [bar=None]",
            """
            class FooBar(AST):
                _attrs = [('bar', 'None', False)]
            """
        )

    def test_multiple_default(self):
        self.check_output(
            "FooBar: [foo=False, bar=True, baz]",
            """
            class FooBar(AST):
                _attrs = [
                    ('foo', 'False', False),
                    ('bar', 'True', False),
                    ('baz', None, False)
                ]
            """
        )

    def test_base(self):
        self.check_output(
            "FooBar(Base): [foo=False, bar=True, baz]",
            """
            class FooBar(Base):
                _attrs = [
                    ('foo', 'False', False),
                    ('bar', 'True', False),
                    ('baz', None, False)
                ]
            """
        )

    def test_multiline(self):
        self.check_output(
            "FooBar: [\n\tfoo=False,\n\t\tbar=True,\nbaz\n]",
            """
            class FooBar(AST):
                _attrs = [
                    ('foo', 'False', False),
                    ('bar', 'True', False),
                    ('baz', None, False)
                ]
            """
        )



if __name__ == '__main__':
    unittest.main(verbosity=1)
