"""Unit-tests for `tree.visitors`
"""

from py2c.tree import Node
from py2c.tree.visitors import RecursiveNodeVisitor, RecursiveNodeTransformer


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


class SimpleVisitor(RecursiveNodeVisitor):

    def __init__(self):
        super().__init__()
        self.visited = []

    def generic_visit(self, node):
        self.visited.append(node.__class__.__name__)
        super().generic_visit(node)

    def visit_BasicNodeCopy(self, node):
        self.visited.append("")


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestRecursiveASTVisitor(Test):
    """tree.visitors.RecursiveNodeVisitor
    """

    def check_visit(self, node, expected_visited):
        visitor = SimpleVisitor()
        retval = visitor.visit(node)
        assert_equal(retval, None)
        assert_equal(visitor.visited, expected_visited)

    def test_visit_and_generic_visit(self):
        yield from self.yield_tests(self.check_visit, [
            (
                "a node without children",
                BasicNode(), ["BasicNode"]
            ),
            (
                "a node without children (calls overidden method)",
                BasicNodeCopy(), [""]
            ),
            (
                "a node with children",
                ParentNode(BasicNode()), ["ParentNode", "BasicNode"]
            ),
            (
                "a node with children (calls overidden method)",
                ParentNode(BasicNodeCopy()), ["ParentNode", ""]
            ),
            (
                "a node with grand children",
                ParentNode(ParentNode(BasicNode())),
                ["ParentNode", "ParentNode", "BasicNode"]
            ),
            (
                "a node with grand children (calls overidden method)",
                ParentNode(ParentNode(BasicNodeCopy())),
                ["ParentNode", "ParentNode", ""]
            ),
            (
                "a node with list of children with grand children "
                "(calls overidden method)",
                ParentNodeWithChildrenList(
                    [ParentNode(BasicNode()), BasicNodeCopy()]
                ),
                ["ParentNodeWithChildrenList", "ParentNode", "BasicNode", ""]
            ),
        ], described=True, prefix="does visit in correct order ")


class TestRecursiveASTTransformer(Test):
    """tree.visitors.RecursiveNodeTransformer
    """


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
