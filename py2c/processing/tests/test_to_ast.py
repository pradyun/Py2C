"""Tests for the Python -> AST translator
"""

import ast
import textwrap

from py2c.processing.to_ast import SourceToAST

from py2c.tests import Test
from nose.tools import assert_equal, assert_raises


class TestPythonSourceToPythonAST(Test):
    """processing.to_ast.SourceToAST
    """

    def check_conversion(self, code, node, error=None):
        """Test the conversion of Python source to Python's AST
        """
        code = textwrap.dedent(code)

        convertor = SourceToAST()

        if node is None:
            if error is None:
                self.fail("Only one of node and error should be non-zero.")
            with assert_raises(error):
                convertor.work(code)
        else:
            if error is not None:
                self.fail("Only one of node and error should be non-zero.")
            assert_equal(ast.dump(convertor.work(code)), ast.dump(node))

    # Could make more extenstive, I guess don't need to
    def test_does_source_to_AST_conversion_correctly(self):
        yield from self.yield_tests(self.check_conversion, [
            [
                "a simple statement",
                "pass", ast.Module(body=[ast.Pass()])
            ]
        ], described=True, prefix="does convert correctly ")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
