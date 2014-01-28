#!/usr/bin/env python
"""Translates Python code into an AST containing type information
"""

import ast
import inspect
from . import dual_ast

__all__ = ["PythonTranslator", "TranslationError", "dual_ast"]
################################################################################
# The implementation below fails the tests. Modify dual_ast and this for passing
# the tests.
################################################################################


class TranslationError(Exception):
    """Raised when a fatal error occurs in Translation
    """
    def __init__(self, msg="", errors=None):
        super(TranslationError, self).__init__()
        self.msg = msg
        self.errors = errors


class PythonTranslator(object):
    """Translates Python code into dual AST

    This is a NodeVisitor that visits the Python AST validates it for conversion
    and creates another AST with type definitions and other stuff, from which
    code is generated.

    """
    def __init__(self):
        super(PythonTranslator, self).__init__()
        self.setup()

    def setup(self):
        self._errors = []
        self.retval = None

    #---------------------------------------------------------------------------
    # Errors
    #---------------------------------------------------------------------------
    def log_error(self, msg, node=None):
        stack = inspect.stack()
        if stack is not None and len(stack) > 1:
            caller_name = stack[1][3]
            # remove 'visit_'
            if caller_name.startswith('visit_'):
                caller_name = caller_name[6:]
            else:  # If it is not a visit_xxx, don't use it
                caller_name = None
        else:
            # Excluded as this can't be achieved during testing.
            caller_name = None  # pragma : no cover

        if caller_name is not None:
            msg = "(Node type: {0}) {1}".format(caller_name, msg)
        if hasattr(node, "lineno"):
            msg += "Check Line ({0}): {1}".format(node.lineno, msg)
        self._errors.append(msg)

    def handle_errors(self):
        if self._errors:
            raise TranslationError(errors=self._errors)

    def get_node(self, code):
        """Get the dual AST from the Python `code`
        Args:
            code: The Python code to be converted to dual AST
        Returns:
            A Py2C AST
        Raises:
            TranslationError if the Python code is not suitable for translation
        """
        self.setup()
        # Get the Python AST
        try:
            node = ast.parse(code)
        except Exception:
            raise TranslationError("Unable to generate AST from Python code")

        di = dual_ast.__dict__.copy()
        retval = eval(ast.dump(node), di, di)

        self.handle_errors()
        return retval
