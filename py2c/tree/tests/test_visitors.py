"""Unit-tests for `tree.visitors`
"""

from py2c import tree
from py2c.tree import visitors

from py2c.tests import Test, data_driven_test
from nose.tools import assert_equal


# TEST:: Add non-node fields

# =============================================================================
# Helper classes
# =============================================================================
class BasicNode(tree.Node):
    _fields = []


class BasicNodeReplacement(tree.Node):
    _fields = []


class BasicNodeWithListReplacement(tree.Node):
    _fields = []


class BasicNodeDeletable(tree.Node):
    _fields = []


class ParentNode(tree.Node):
    _fields = [
        ('child', tree.Node, 'OPTIONAL'),
    ]


class ParentNodeWithChildrenList(tree.Node):
    """Node with list of nodes as field
    """
    _fields = [
        ('child', tree.Node, 'ZERO_OR_MORE'),
    ]


# -----------------------------------------------------------------------------
# Concrete Visitors used for testing
# -----------------------------------------------------------------------------
class VisitOrderCheckingVisitor(visitors.RecursiveNodeVisitor):

    def __init__(self):
        super().__init__()
        self.visited = []

    def generic_visit(self, node):
        self.visited.append(node.__class__.__name__)
        super().generic_visit(node)

    def visit_BasicNodeReplacement(self, node):
        self.visited.append("visited Copy!")


class AccessPathCheckingVisitor(visitors.RecursiveNodeVisitor):

    def __init__(self):
        super().__init__()
        self.recorded_access_path = None

    def visit_BasicNode(self, node):
        self.recorded_access_path = self.access_path[:]


class EmptyTransformer(visitors.RecursiveNodeTransformer):
    pass


class VisitOrderCheckingTransformer(visitors.RecursiveNodeTransformer):

    def __init__(self):
        super().__init__()
        self.visited = []

    def generic_visit(self, node):
        self.visited.append(node.__class__.__name__)
        return super().generic_visit(node)

    def visit_BasicNodeReplacement(self, node):
        self.visited.append("visited Copy!")
        return node


class AccessPathCheckingTransformer(visitors.RecursiveNodeTransformer):

    def __init__(self):
        super().__init__()
        self.recorded_access_path = None

    def visit_BasicNode(self, node):
        self.recorded_access_path = self.access_path[:]
        return node


class TransformationCheckingTransformer(visitors.RecursiveNodeTransformer):

    def visit_BasicNode(self, node):
        return BasicNodeReplacement()

    def visit_BasicNodeDeletable(self, node):
        return None  # Delete this node

    def visit_BasicNodeReplacement(self, node):
        return self.NONE_DEPUTY  # Replace this node with None

    def visit_BasicNodeWithListReplacement(self, node):
        return [BasicNode(), BasicNodeReplacement()]


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestRecursiveASTVisitor(Test):
    """py2c.tree.visitors.RecursiveNodeVisitor
    """
    context = globals()

    @data_driven_test("visitors-visitor_order.yaml", prefix="visit order of ")
    def test_visit_order(self, node, order):
        to_visit = self.load(node)

        # The main stuff
        visitor = VisitOrderCheckingVisitor()
        retval = visitor.visit(to_visit)

        assert_equal(retval, None)
        assert_equal(visitor.visited, order)

    @data_driven_test("visitors-access_path.yaml", prefix="access path on visit of ")
    def test_access_path(self, node, access):
        to_visit = self.load(node)
        access_path = self.load(access)

        # The main stuff
        visitor = AccessPathCheckingVisitor()
        retval = visitor.visit(to_visit)

        assert_equal(retval, None)
        assert_equal(visitor.recorded_access_path, access_path)


class TestRecursiveASTTransformer(Test):
    """py2c.tree.visitors.RecursiveNodeTransformer
    """
    context = globals()

    @data_driven_test("visitors-visitor_order.yaml", prefix="empty transformer does not transform ")
    def test_empty_transformer(self, node, order):
        to_visit = self.load(node)

        # The main stuff
        visitor = EmptyTransformer()
        retval = visitor.visit(to_visit)

        assert_equal(to_visit, retval)

    @data_driven_test("visitors-visitor_order.yaml", prefix="visit order of ")
    def test_visit_order(self, node, order):
        to_visit = self.load(node)

        # The main stuff
        visitor = VisitOrderCheckingTransformer()
        retval = visitor.visit(to_visit)

        assert_equal(to_visit, retval)
        assert_equal(visitor.visited, order)

    @data_driven_test("visitors-access_path.yaml", prefix="access path on visit of ")
    def test_access_path(self, node, access):
        to_visit = self.load(node)
        access_path = self.load(access)

        # The main stuff
        visitor = AccessPathCheckingTransformer()
        retval = visitor.visit(to_visit)

        assert_equal(retval, to_visit)
        assert_equal(visitor.recorded_access_path, access_path)

    @data_driven_test("visitors-transform.yaml", prefix="transformation of ")
    def test_transformation(self, node, expected):
        to_visit = self.load(node)
        expected_node = self.load(expected)

        # The main stuff
        visitor = TransformationCheckingTransformer()
        retval = visitor.visit(to_visit)

        assert_equal(retval, expected_node)


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
