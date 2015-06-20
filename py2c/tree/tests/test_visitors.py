"""Unit-tests for `tree.visitors`
"""

from py2c.tests import Test, data_driven_test
from nose.tools import assert_equal

import py2c.tree.tests.data_visitors as data


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestRecursiveASTVisitor(Test):
    """py2c.tree.visitors.RecursiveNodeVisitor
    """

    @data_driven_test(data.RecursiveNodeVisitor_visit_order_cases, True, "visits in correct order: ")  # noqa
    def test_visit_order(self, node, expected_visited):
        visitor = data.SimpleVisitor()
        retval = visitor.visit(node)
        assert_equal(retval, None)
        assert_equal(visitor.visited, expected_visited)


class TestRecursiveASTTransformer(Test):
    """py2c.tree.visitors.RecursiveNodeTransformer
    """


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
