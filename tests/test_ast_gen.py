import textwrap
import unittest
import difflib

import support

import py2c._ast_gen as ast_gen
from py2c._ast_gen import Node, Attr
import py2c.dual_ast as dual_ast

class DummyNode(dual_ast.AST):
    def __init__(self, attrs=None, *args, **kwargs):
        if attrs is None:
            attrs = []
        self._attrs = attrs
        super(DummyNode, self).__init__(*args, **kwargs)


class ParserTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for Parsing of structures"""

    def setUp(self):
        self.parser = ast_gen.Parser()

    def template(self, test_string, expected):
        self.test_string = test_string
        self.parser.prepare(str(test_string))
        self.assertEqual(self.parser.data, expected)

    def assertMultiLineEqual(self, first, second, msg=None):
        """Assert that two multi-line strings are equal.

        If they aren't, show a nice diff.
        """
        self.assertTrue(isinstance(first, str),
                'First argument is not a string')
        self.assertTrue(isinstance(second, str),
                'Second argument is not a string')

        if first != second:
            message = ''.join(difflib.ndiff(first.splitlines(True),
                                                second.splitlines(True)))
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)

class CommentTestCase(ParserTestCase):
    """Tests for Parser parsing comments"""

    def test_comment_empty_line(self):
        "Checks if Parser handles empty lines with comments correctly"
        self.template(
            "#test: [a,string]",
            []
        )

    def test_comment_no_arg(self):
        "Checks if Parser handles Nodes with comments correctly"
        self.template(
            "foo: [] #test: [a,string]",
            [Node('foo', [])]
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
            [Node('foo', [Attr('bar', None, None, False)])]
        )

    def test_property_multi_arg(self):
        self.template(
            "foo: [bar, baz]",
            [Node('foo', [
                Attr('bar', None, None, False), Attr('baz', None, None, False)])]
        )

    def test_property_1arg_default(self):
        self.template(
            "foo: [bar=None]",
            [Node('foo', [Attr('bar', 'None', None, False)])]
        )

    def test_property_multi_arg_default(self):
        self.template(
            "foo: [bar, baz=None]",
            [Node('foo', [
                Attr('bar', None, None, False),
                Attr('baz', 'None', None, False)]
            )]
        )

    def test_invalid_object_to_prepare(self):
        self.assertRaises(TypeError, self.parser.prepare, 1)


class GeneratesupportTestCase(ParserTestCase):
    """Tests for Generatesupport of classes from Data"""

    def get_result(self, data):
        self.parser.data = data
        di = {}
        self.parser.setup_module(di)
        return di

    def basic_checks(self, di, name):
        self.assertEqual(len(di.keys()), 1,
                         'Invalid number of properties generated')
        self.assertEqual(list(di.keys())[0], name, 'The variable name is not same')
        self.assertEqual(di[name].__name__, name, "Names don't match")

    def check_instance(self, instance, args):
        self.assertEqual(instance._fields, args, "Fields don't match")
        for i in instance._fields:
            self.assertTrue(hasattr(instance, i), '{0!r} attribute is missing'.format(i))
        self.assertEqual(instance._fields, args, "Fields don't match")

    def test_verbose_output(self):
        text = "foo: [bar]"
        self.parser.prepare(text)
        self.parser.prefix = ""
        # create a fake file
        fake = support.StringIO()
        self.parser.write_module(fake)
        result = fake.getvalue()



        self.assertMultiLineEqual(result.strip(), textwrap.dedent("""
            class foo(AST):
                def __init__(self, *args, **kwargs):
                    self._attrs = [Attr('bar', None, None, False)]
                    super(foo, self).__init__(*args, **kwargs)
            """).strip()
        )

    def test_indent1(self):
        "Tests for indent function"
        self.assertEqual(ast_gen.indent("foo"), '    foo')
        self.assertEqual(ast_gen.indent("foo\nbar"), '    foo\n    bar')
        self.assertEqual(ast_gen.indent("foo\n"), '    foo')
        self.assertEqual(ast_gen.indent("\nfoo"), '    foo')

if __name__ == '__main__':
    unittest.main(verbosity=1)
