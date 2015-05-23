"""Tests for the RecursiveTreeVisitor.
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

from py2c.tree import Node
from py2c.tree.visitors import RecursiveTreeVisitor, RecursiveTreeTransformer


from py2c.tests import Test
from nose.tools import assert_equal


# -----------------------------------------------------------------------------
# Test helpers
# -----------------------------------------------------------------------------
class BasicNode(Node):
    """Basic node
    """
    _fields = []


class BasicNodeCopy(Node):
    """Equivalent but not equal to BasicNode
    """
    _fields = []


class ParentNode(Node):
    """Node with another node as child
    """
    _fields = [
        ('child', Node, 'NEEDED'),
    ]


class ParentNodeWithChildrenList(Node):
    """Node with another node as child
    """
    _fields = [
        ('child', Node, 'ONE_OR_MORE'),
    ]


class MySimpleVisitor(RecursiveTreeVisitor):

    def __init__(self):
        super().__init__()
        self.visited = []

    def generic_visit(self, node):
        self.visited.append(node.__class__.__name__)
        super().generic_visit(node)

    def visit_BasicNodeCopy(self, node):
        self.visited.append("Works!!")


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestRecursiveASTVisitor(Test):
    """tree.RecursiveTreeVisitor
    """

    def check_visit(self, node, expected_visited):
        visitor = MySimpleVisitor()
        retval = visitor.visit(node)
        assert_equal(retval, None)
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


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestRecursiveASTTransformer(Test):
    """tree.RecursiveTreeTransformer
    """


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
