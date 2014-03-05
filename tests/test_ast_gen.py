import unittest
import difflib
from textwrap import dedent

import support

import py2c._ast_gen as ast_gen
from py2c._ast_gen import Node, Attr


class ParserTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for Parsing of structures"""

    def setUp(self):
        self.parser = ast_gen.ConfigFileLoader()

    def template(self, test_string, expected):
        self.parser.prepare(str(test_string))
        self.assertEqual(self.parser.data, expected)

    def assertMultiLineEqual(self, first, second, msg=None, files=None):
        """Assert that two multi-line strings are equal.

        If they aren't, show a nice diff.
        """
        if not isinstance(first, str):
            raise TypeError('First positional argument is not a string')
        if not isinstance(second, str):
            raise TypeError('Second positional argument is not a string')

        if first != second:
            message = ''.join(difflib.unified_diff(
                first.splitlines(True),
                second.splitlines(True),
            ))

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
            [Node('foo', [Attr('bar', None)])]
        )

    def test_property_multi_arg(self):
        self.template(
            "foo: [bar, baz]",
            [Node('foo', [
                Attr('bar', None), Attr('baz', None)])]
        )

    def test_property_1arg_default(self):
        self.template(
            "foo: [bar=None]",
            [Node('foo', [Attr('bar', 'None')])]
        )

    def test_property_multi_arg_default(self):
        self.template(
            "foo: [bar, baz=None]",
            [Node('foo', [
                Attr('bar', None),
                Attr('baz', 'None')
            ])]
        )

    def test_default_conversion(self):
        "Tests for default values' conversion to sources"
        self.template(
            'foo: [a=True, b=False, c=None, d=[], e=(), f="", g="\n"]',
            [Node('foo', [
                Attr('a', 'True'),
                Attr('b', 'False'),
                Attr('c', 'None'),
                Attr('d', '[]'),
                Attr('e', '()'),
                Attr('f', '""'),
                Attr('g', '"\n"'),
            ])]
        )

    def test_invalid_object_to_prepare(self):
        errors = [TypeError, ast_gen.LexerError, ast_gen.ParsingError]
        args = [1, "foo: [$x]", "foo: [x y]"]
        # Iterate over errors and arguments
        for err, arg in zip(errors, args):
            self.assertRaises(err, self.parser.prepare, arg)


class GenerationTestCase(ParserTestCase):
    """Tests for generated sources
    """
    # Override 'template' for this test has a different one
    # Still is a ParserTestCase
    def template(self, text, expected_output):
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
            dedent(expected_output).strip(), fake.getvalue().strip()
        )

    def test_single_nodefault(self):
        self.template(
            "FooBar: [bar]",
            """
            class FooBar(AST):
                _fields = ['bar']

                def __init__(self, bar):
                    self.bar = bar
            """
        )

    def test_multiple_nodefault(self):
        self.template(
            "FooBar: [bar, baz]",
            """
            class FooBar(AST):
                _fields = ['bar', 'baz']

                def __init__(self, bar, baz):
                    self.bar = bar
                    self.baz = baz
            """
        )

    def test_single_default(self):
        self.template(
            "FooBar: [bar=None]",
            """
            class FooBar(AST):
                _fields = ['bar']

                def __init__(self, bar=None):
                    self.bar = bar
            """
        )

    def test_multiple_default(self):
        self.template(
            "FooBar: [foo, bar=True, baz=False]",
            """
            class FooBar(AST):
                _fields = ['foo', 'bar', 'baz']

                def __init__(self, foo, bar=True, baz=False):
                    self.foo = foo
                    self.bar = bar
                    self.baz = baz
            """
        )

    def test_base(self):
        self.template(
            "FooBar(Base): [foo, bar=True, baz=False]",
            """
            class FooBar(Base):
                _fields = ['foo', 'bar', 'baz']

                def __init__(self, foo, bar=True, baz=False):
                    self.foo = foo
                    self.bar = bar
                    self.baz = baz
            """
        )

    def test_multiline(self):
        self.template(
            "FooBar: [\n\tfoo,\n\t\tbar\n=\tTrue\n,baz=False]",
            """
            class FooBar(AST):
                _fields = ['foo', 'bar', 'baz']

                def __init__(self, foo, bar=True, baz=False):
                    self.foo = foo
                    self.bar = bar
                    self.baz = baz
            """
        )

    def test_more_than_80_chars(self):
        letters = str(list("abcdefghijklmnopqrstuvwxyz"))[1:-1]
        list_content = letters.replace(", ", ",\n" + (" " * 8))
        formatted_letters = "[\n        " + list_content + "\n    ]"
        self.template(
            """FooBar: [
                a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u,
                v, w, x, y, z
            ]""",
            dedent("""
            class FooBar(AST):
                _fields = {}

                def __init__(self, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z):  # noqa
                    self.a = a
                    self.b = b
                    self.c = c
                    self.d = d
                    self.e = e
                    self.f = f
                    self.g = g
                    self.h = h
                    self.i = i
                    self.j = j
                    self.k = k
                    self.l = l
                    self.m = m
                    self.n = n
                    self.o = o
                    self.p = p
                    self.q = q
                    self.r = r
                    self.s = s
                    self.t = t
                    self.u = u
                    self.v = v
                    self.w = w
                    self.x = x
                    self.y = y
                    self.z = z
            """).format(formatted_letters)
        )


class ReprTestCase(unittest.TestCase):
    """Tests for __repr__ methods of the helper classes"""
    def test_repr_Attr(self):
        attr1 = Attr("a", "None")
        attr2 = Attr("a", None)
        attr3 = Attr("a", [])
        self.assertEqual(repr(attr1), "Attr('a', 'None')")
        self.assertEqual(repr(attr2), "Attr('a', None)")
        self.assertEqual(repr(attr3), "Attr('a', [])")

    def test_repr_Node(self):
        node1 = Node("a", [Attr('a', [])])
        node2 = Node("a", [])
        self.assertEqual(repr(node1), "Node('a', [Attr('a', [])])")
        self.assertEqual(repr(node2), "Node('a', [])")


if __name__ == '__main__':
    unittest.main(buffer=True)
