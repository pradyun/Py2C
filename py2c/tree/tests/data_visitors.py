"""Data for unit-tests for `py2c.tree.visitors`
"""

from py2c import tree
from py2c.tree import visitors


# =============================================================================
# Helper classes
# =============================================================================
class BasicNode(tree.Node):
    """Basic node
    """
    _fields = []


class BasicNodeCopy(tree.Node):
    """Equivalent but not equal to BasicNode
    """
    _fields = []


class ParentNode(tree.Node):
    """Node with another node as child
    """
    _fields = [
        ('child', tree.Node, 'NEEDED'),
    ]


class ParentNodeWithChildrenList(tree.Node):
    """Node with another node as child
    """
    _fields = [
        ('child', tree.Node, 'ONE_OR_MORE'),
    ]


class SimpleVisitor(visitors.RecursiveNodeVisitor):

    def __init__(self):
        super().__init__()
        self.visited = []

    def generic_visit(self, node):
        self.visited.append(node.__class__.__name__)
        super().generic_visit(node)

    def visit_BasicNodeCopy(self, node):
        self.visited.append("")


# =============================================================================
# Tests
# =============================================================================
RecursiveNodeVisitor_visit_order_cases = [
    (
        "node without children",
        BasicNode(), ["BasicNode"]
    ),
    (
        "node without children (calls overidden method)",
        BasicNodeCopy(), [""]
    ),
    (
        "node with children",
        ParentNode(BasicNode()), ["ParentNode", "BasicNode"]
    ),
    (
        "node with children (calls overidden method)",
        ParentNode(BasicNodeCopy()), ["ParentNode", ""]
    ),
    (
        "node with grand children",
        ParentNode(ParentNode(BasicNode())),
        ["ParentNode", "ParentNode", "BasicNode"]
    ),
    (
        "node with grand children (calls overidden method)",
        ParentNode(ParentNode(BasicNodeCopy())),
        ["ParentNode", "ParentNode", ""]
    ),
    (
        "node with list of children with grand children "
        "(calls overidden method)",
        ParentNodeWithChildrenList(
            [ParentNode(BasicNode()), BasicNodeCopy()]
        ),
        ["ParentNodeWithChildrenList", "ParentNode", "BasicNode", ""]
    ),
]
