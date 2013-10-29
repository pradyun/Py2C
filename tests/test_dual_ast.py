#!/usr/bin/env python

import sys
import textwrap
import unittest

import support
import py2c.dual_ast as dual_ast


class DummyNode(dual_ast.AST):
    def __init__(self, attrs=None, *args, **kwargs):
        if attrs is None:
            attrs = []
        self._attrs = attrs
        super(DummyNode, self).__init__(*args, **kwargs)

# -----------------------------------
class ASTTestCase(unittest.TestCase):
    """Tests for AST node"""

    def test_init1(self):
        "A no-subclass directly invoked"
        with self.assertRaises(AttributeError):
            dual_ast.AST()

    def test_equality_equal1(self):
        "Test for equality for really equal Nodes"
        attrs = [("foo", None, None, False), ('bar', 'list', '[]', True)]

        node1 = DummyNode(attrs)
        node2 = DummyNode(attrs)

        self.assertEqual(node1, node2)

    def test_equality_equal2(self):
        "Test for equality with node when it has children nodes"
        node1 = DummyNode(dest=DummyNode(id='foo'), values=[],
                                    sep=' ', end='\n')
        node2 = DummyNode(dest=DummyNode(id='foo'), values=[],
                                    sep=' ', end='\n')
        self.assertEqual(node1, node2)

    def test_equality_with_extra_attrs(self):
        "Test for (in)equality on nodes with in-equal attributes"
        node1 = DummyNode([("foo", None, None, False)])
        node2 = DummyNode([("foo", None, None, False), ("bar", None, None, False)])

        self.assertNotEqual(node1, node2, str(node1._attrs) + str(node2._attrs))


    def test_equality_diff_type(self):
        "Test for inequality on the basis of type"
        node1 = DummyNode([])

        self.assertNotEqual(node1, "I'm not equal to a Node")

if __name__ == '__main__':
    unittest.main()
