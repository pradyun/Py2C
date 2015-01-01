"""Tests for the RecursiveASTVisitor.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c import ast

from py2c.tests import Test
from nose.tools import assert_equal


#------------------------------------------------------------------------------
# Test helpers
#------------------------------------------------------------------------------
class BasicNode(ast.AST):
    """Basic node
    """
    _fields = []


class BasicNodeCopy(ast.AST):
    """Equivalent but not equal to BasicNode
    """
    _fields = []


class ParentNode(ast.AST):
    """Node with another node as child
    """
    _fields = [
        ('child', ast.AST, ast.NEEDED),
    ]


class ParentNodeWithChildrenList(ast.AST):
    """Node with another node as child
    """
    _fields = [
        ('child', ast.AST, ast.ONE_OR_MORE),
    ]


class MyVisitor(ast.RecursiveASTVisitor):

    def __init__(self):
        super().__init__()
        self.visited = []

    def generic_visit(self, node):
        self.visited.append(node.__class__.__name__)
        super().generic_visit(node)
        return node

    def visit_BasicNodeCopy(self, node):
        self.visited.append("Works!!")
        return node


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestRecursiveASTVisitor(Test):
    """py2c.ast.RecursiveASTVisitor
    """

    def check_visit(self, node, expected_visited):
        visitor = MyVisitor()
        retval = visitor.visit(node)
        assert_equal(node, retval)
        assert_equal(visitor.visited, expected_visited)

    def test_visit_and_generic_visit(self):
        yield from self.yield_tests(self.check_visit, [
            (
                "simple node without children",
                BasicNode(), ["BasicNode"]
            ),
            (
                "simple node, overidden method",
                BasicNodeCopy(), ["Works!!"]
            ),
            (
                "parent node, overidden method",
                ParentNode(BasicNode()), ["ParentNode", "BasicNode"]
            ),
            (
                "parent of parent node, overidden method",
                ParentNode(ParentNode(BasicNode())),
                ["ParentNode", "ParentNode", "BasicNode"]
            ),
            (
                "parent of parent node, overidden method",
                ParentNode(BasicNodeCopy()),
                ["ParentNode", "Works!!"]
            ),
            (
                "parent of parent node, overidden method",
                ParentNodeWithChildrenList(
                    [ParentNode(BasicNode()), BasicNodeCopy()]
                ),
                ["ParentNodeWithChildrenList", "ParentNode", "BasicNode", "Works!!"]
            ),
        ], described=True, prefix="visit ")

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
