"""Tests for the Python -> AST translator
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

import ast
import textwrap

from py2c.pre_processing.to_ast import (
    SourceToAST, SourceToASTTranslationError
)

from py2c.tests import Test
from nose.tools import assert_equal, assert_raises


class TestPythonSourceToPythonAST(Test):
    """py2c.pre_processing.to_ast.SourceToAST
    """

    # Test the conversion of some simple Python source to Python's AST
    def check_conversion(self, code, node, error=None):
        code = textwrap.dedent(code)

        convertor = SourceToAST()

        if node is None:
            if error is None:
                raise AssertionError("Only one of node and error should be non-zero.")
            with assert_raises(error):
                convertor.work(code)
        else:
            if error is not None:
                raise AssertionError("Only one of node and error should be non-zero.")
            assert_equal(ast.dump(convertor.work(code)), ast.dump(node))

    # Could make more extenstive, I guess don't need to
    def test_conversion(self):
        yield from self.yield_tests(self.check_conversion, [
            [
                "simple statement conversion",
                "pass", ast.Module(body=[ast.Pass()])
            ]
        ], described=True, prefix="check conversion of ")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
