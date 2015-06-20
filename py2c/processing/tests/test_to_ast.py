"""Unit-tests for `py2c.processing.to_ast`
"""

import ast
import textwrap

from py2c.processing.to_ast import SourceToAST, SourceToASTTranslationError

from py2c.tests import Test, data_driven_test
from nose.tools import assert_equal, assert_raises


class TestPythonSourceToPythonAST(Test):
    """py2c.processing.to_ast.SourceToAST
    """

    # Could make more extensive, I guess don't need to
    @data_driven_test(described=True, prefix="converts valid input correctly: ", data=[  # noqa
        ["a pass statement", "pass", ast.Module(body=[ast.Pass()])]
    ])
    def test_valid_input_cases(self, code, node):
        assert_equal(
            ast.dump(SourceToAST().work(textwrap.dedent(code))),
            ast.dump(node)
        )

    @data_driven_test(described=True, prefix="raises error when given: ", data=[  # noqa
        ["invalid code", "$", SourceToASTTranslationError]
    ])
    def test_invalid_input_cases(self, code, error):
        with assert_raises(error):
            SourceToAST().work(textwrap.dedent(code))

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
