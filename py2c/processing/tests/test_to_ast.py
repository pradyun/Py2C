"""Unit-tests for `py2c.processing.to_ast`
"""

import ast
import difflib

from py2c.utils import is_py2c_temp_var
from py2c.tree.visitors import RecursiveNodeTransformer
from py2c.processing.to_ast import SourceToAST, SourceToASTTranslationError

from py2c.tests import Test, data_driven_test
from nose.tools import assert_equal, assert_raises


class NodeNameSimplifier(RecursiveNodeTransformer):
    """Makes the temporary names used predictable.
    """

    def __init__(self):
        RecursiveNodeTransformer.__init__(self, ast.AST, ast.iter_fields)

    def visit(self, node):
        self._temp_var_names = []
        return super().visit(node)

    def visit_Name(self, node):
        self._visit_children(node)

        if is_py2c_temp_var(node.id):
            if node.id not in self._temp_var_names:
                self._temp_var_names.append(node.id)
            node.id = "_py2c_val_{}".format(self._temp_var_names.index(node.id) + 1)

        return node


class TestPythonSourceToPythonAST(Test):
    """py2c.processing.to_ast.SourceToAST
    """

    maxDiff = None
    name_simplifier = NodeNameSimplifier()

    def replace_py2c_variables_with_predictables(self, node):
        self.name_simplifier.visit(node)

    def assert_nodes_equal(self, node1, node2):
        a = ast.dump(node1)
        b = ast.dump(node2)
        if a != b:
            self.fail("\n".join(difflib.unified_diff(a.splitlines(), b.splitlines(), "node1", "node2")))

    @data_driven_test("ast-level-transformations.yaml")
    def test_ast_level_tranformations(self, input_text, output_text):
        expect_node = ast.parse(output_text)

        s2a = SourceToAST()
        result = s2a.work(input_text)

        self.replace_py2c_variables_with_predictables(result)
        self.assert_nodes_equal(expect_node, result)


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
