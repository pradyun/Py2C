"""Translates Python code into Python's built-in AST.
"""

import ast

from py2c.abc.worker import Worker
from py2c.processing import ProcessingError
from py2c.tree.visitors import RecursiveNodeTransformer

from py2c.utils import get_temp_variable_name

__all__ = ["SourceToASTTranslationError", "SourceToAST"]


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class SourceToASTTranslationError(ProcessingError):
    """Raised when fatal error(s) occur in the Translation of source-code to AST.
    """

    def __init__(self):
        super().__init__("Couldn't convert source-code to AST.")


# -----------------------------------------------------------------------------
# Translator
# -----------------------------------------------------------------------------
class SourceToAST(Worker, RecursiveNodeTransformer):
    """Translates Python code into an simplified AST
    """

    def __init__(self):
        Worker.__init__(self)
        RecursiveNodeTransformer.__init__(self, ast.AST, ast.iter_fields)

    def work(self, code):
        """Translate the passed code into a Python AST and simplify it.
        """
        try:
            node = ast.parse(code)
        except Exception as e:
            raise SourceToASTTranslationError() from e
        else:
            return node
