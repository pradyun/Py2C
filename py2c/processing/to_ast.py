"""Translates Python code into Python's built-in AST.
"""

import ast

from py2c.abc.worker import Worker
from py2c.processing import ProcessingError

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
class SourceToAST(Worker):
    """Translates Python code into AST
    """

    def work(self, code):
        """Translate the passed code into a valid Python AST, if the code is valid.
        """
        try:
            node = ast.parse(code)
        except Exception as e:
            raise SourceToASTTranslationError() from e
        else:
            return node
