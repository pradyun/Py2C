#!/usr/bin/env python

import StringIO
import unittest

import support

with support.project_imports():
    import c_ast

# ----------------------------------
class ParserTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for Parsing of structures"""
    def setUp(self):
        self.parser = c_ast.Parser()

    def prepare(self, test_string):
        self.test_string = test_string
        self.parser.prepare(StringIO.StringIO(test_string))
        return self.parser.data

class CommentTestCase(ParserTestCase):
    """Tests for Parser parsing comments"""
    def test_comment_empty_line(self):
        "Checks: Parser handles empty lines with comments correctly"
        data = self.prepare("#test: a,string")
        self.assertEqual(data, [])

    def test_comment_no_arg_no_space(self):
        "Checks: Parser handles no argument Nodes with comments correctly"
        data = self.prepare("foo:#test: a,string")
        self.assertEqual(data, [['foo', []]])

    def test_comment_no_arg_with_spaces(self):
        "Checks: Parser handles no argument Nodes with comments correctly"
        data = self.prepare("foo: #test: a,string")
        self.assertEqual(data, [['foo', []]])

    def test_comment_1arg_no_space(self):
        "Checks: Parser handles 1 argument Nodes with comments correctly"
        data = self.prepare("foo: bar#test: a,string")
        self.assertEqual(data, [['foo', ['bar']]])

    def test_comment_1arg_with_spaces(self):
        "Checks: Parser handles 1 argument Nodes with comments correctly"
        data = self.prepare("foo: bar #test: a,string")
        self.assertEqual(data, [['foo', ['bar']]])

    def test_comment_multi_arg_no_space(self):
        "Checks: Parser handles multi argument Nodes with comments correctly"
        data = self.prepare("foo: bar, baz#test: a,string")
        self.assertEqual(data, [['foo', ['bar', 'baz']]])

    def test_comment_multi_arg_with_spaces(self):
        "Checks: Parser handles multi argument Nodes with comments correctly"
        data = self.prepare("foo: bar, baz #test: a,string")
        self.assertEqual(data, [['foo', ['bar', 'baz']]])

class PropertyTestCase(ParserTestCase):
    """Tests for Parser's parsing of Properties"""
    def test_property_empty(self):
        data = self.prepare("foo:")
        self.assertEqual(data, [['foo', []]])

    def test_property_1arg(self):
        data = self.prepare("foo: bar")
        self.assertEqual(data, [['foo', ['bar']]])

    def test_property_multi_arg(self):
        data = self.prepare("foo: bar, baz")
        self.assertEqual(data, [['foo', ['bar', 'baz']]])

    def test_property_1arg_default(self):
        data = self.prepare("foo: bar=None")
        self.assertEqual(data, [['foo', ['bar=None']]])

    def test_property_multi_arg_default(self):
        data = self.prepare("foo: bar, baz=None")
        self.assertEqual(data, [['foo', ['bar', 'baz=None']]])

    def test_invalid_object_to_prepare(self):
        self.assertRaises(TypeError, self.parser.prepare, 1)

# There really is only one data structure which is generated,
# so One test case is enough
class GenerationTestCase(ParserTestCase):
    """Tests for Generation of classes from Data"""
    def get_result(self, data):
        self.parser.data = data
        di = {}
        self.parser.setup_module(di)
        return di

    def basic_checks(self, di, name):
        self.assertEqual(len(di.keys()), 1,
                         'Invalid number of properties generated')
        self.assertEqual(di.keys()[0], name, 'The variable name is not same')
        self.assertEqual(di[name].__name__, name, "Names don't match")

    def check_instance(self, instance, args):
        self.assertEqual(instance._fields, args, "Fields don't match")
        for i in instance._fields:
            self.assertTrue(hasattr(instance, i), '{0!r} attribute is missing'.format(i))
        self.assertEqual(instance._fields, args, "Fields don't match")

    def test_property_no_arg(self):
        di = self.get_result([['foo', []]])
        self.basic_checks(di, 'foo')

        # Check __init__ function arguments
        self.assertRaises(TypeError, di['foo'], 1)
        self.assertRaises(TypeError, di['foo'], 1, 2)

        instance = di['foo']() # No arg call
        self.check_instance(instance, [])

    def test_property_1arg(self):
        di = self.get_result([['foo', ['bar']]])
        self.basic_checks(di, 'foo')

        # Check __init__ function arguments
        self.assertRaises(TypeError, di['foo'])
        self.assertRaises(TypeError, di['foo'], 1, 2)

        instance = di['foo'](1) # 1 arg call
        self.check_instance(instance, ['bar'])

    def test_property_multi_arg(self):
        di = self.get_result([['foo', ['bar', 'baz']]])
        self.basic_checks(di, 'foo')

        # Check __init__ function arguments
        self.assertRaises(TypeError, di['foo'])
        self.assertRaises(TypeError, di['foo'], 1)

        instance = di['foo'](1, 2) # 2 arg call
        self.check_instance(instance, ['bar', 'baz'])

    # Given anything with a __dict__ attribute
    def test_generator_not_dict(self):
        data = [['foo', []]]
        cls = type('cls', (object,), {})
        obj = cls()
        self.parser.data = data
        self.parser.setup_module(obj)
        self.basic_checks(obj.__dict__, 'foo')

# -----------------------------------
class ASTTestCase(unittest.TestCase):
    """Tests for AST node"""

    def test_equality_equal(self):
        "Test for equality for really equal Nodes"
        node1 = node2 = c_ast.AST()
        # add fields and attributes
        node1._fields = map(chr, range(97, 103))
        di = {chr(i): i for i in range(97, 103)}
        node1.__dict__.update(di)

        self.assertEqual(node1, node2)

    def test_equality_with_extra_attrs(self):
        "Test for equality on nodes wth equal fields, and extra attributes"
        node1 = c_ast.AST()
        node2 = c_ast.AST()

        # add fields and attributes
        node1._fields = map(chr, range(97, 103))
        di = {chr(i): i for i in range(97, 103)}
        node1.__dict__.update(di)
        node2._fields = node1._fields
        di = {chr(i): i for i in range(97, 104)}
        node2.__dict__.update(di)

        self.assertEqual(node1, node2)

    def test_equality_diff_fields(self):
        "Test for inequality on the basis of _fields attribute"
        node1 = c_ast.AST()
        node2 = c_ast.AST()

        # add fields and attributes
        node1._fields = map(chr, range(97, 103))
        di = {chr(i): i for i in range(97, 103)}
        node1.__dict__.update(di)
        node2.__dict__.update(di)
        node2._fields = node1._fields + ["i_will_make_the_two_equal"]

        self.assertNotEqual(node1, node2)

    def test_equality_diff_type(self):
        "Test for equality on the basis of type"
        node1 = c_ast.AST()

        self.assertNotEqual(node1, "I'm not equal to a Node")

    def test_equality_diff_attrs(self):
        "Test for equality on the basis of attributes"
        node1 = c_ast.AST()
        node2 = c_ast.AST()

        # add fields and attributes
        node1._fields = map(chr, range(97, 103))
        di = {chr(i): i for i in range(97, 103)}
        node1.__dict__.update(di)
        node2._fields = node1._fields
        di = {chr(i): i for i in range(98, 104)}
        node2.__dict__.update(di)

        self.assertNotEqual(node1, node2)

if __name__ == '__main__':
    unittest.main()
