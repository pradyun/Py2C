"""Translates Python code into an AST containing type and control-flow information.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import ast

import py2c.ast.python as py_ast
from py2c.ast import RecursiveASTVisitor


#------------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------------
class TranslationError(Exception):
    """Raised when a fatal error occurs in Translation
    """

    def __init__(self, msg="", errors=None):
        super().__init__(msg, errors)
        self.msg = msg
        self.errors = errors


#------------------------------------------------------------------------------
# Translator
#------------------------------------------------------------------------------
class PythonToAST(RecursiveASTVisitor):
    """Translates Python code into Py2C AST
    """

    def __init__(self):
        super().__init__(root_class=ast.AST, iter_fields=ast.iter_fields)
        self._reset()

    def _reset(self):
        self.errors = []
        # Basic knowledge of what names have been used
        self.names_used = set()  # Make note that the name has been used.

    # Errors
    def _log_error(self, msg, lineno=None):
        """Log an error in the provided code
        """
        if lineno is not None:
            msg = "Line {0}: {1}".format(lineno, msg)
        self.errors.append(msg)

    def _handle_errors(self):
        """Handle the errors, if any, logged during generation
        """
        if not self.errors:
            return
        # print(self.errors)
        raise TranslationError(errors=self.errors)

    #==========================================================================
    # API
    #==========================================================================
    def convert(self, code):
        """Get the Py2C AST from the Python ``code``

        Arguments:
            code: The Python code to be converted to Py2C AST
        Returns:
            A Py2C AST
        Raises:
            ``TranslationError`` if the code is invalid Python code or there
            were errors during translation
        """
        self._reset()
        # Get the Python AST
        try:
            node = ast.parse(code)
        except Exception:
            raise TranslationError("Invalid Python code provided.")
        else:
            # print("AST:    ", ast.dump(node))
            retval = self.visit(node)
            self._handle_errors()
            return retval

    #==========================================================================
    # Helpers
    #==========================================================================
    def generic_visit(self, node):
        return self.convert_to_python_node(node)

    def convert_to_python_node(self, node):
        """Convert ``ast`` node (and children) into ``py2c.ast`` nodes.
        """
        self.visit_children(node)

        node_name = node.__class__.__name__
        py_node = getattr(py_ast, node_name)

        retval = py_node(**dict(ast.iter_fields(node)))
        # retval.finalize()

        return retval

    #==========================================================================
    # Visitors, only for specially handled nodes
    #==========================================================================
    def visit_Name(self, node):
        self.names_used.add(node.id)  # Make note that the name has been used.

        # coverage excluded as condition is never True in Python 3.4
        if node.id in ["True", "False", "None"]:  # coverage: no partial
            return py_ast.NameConstant(eval(node.id))  # coverage: not missing

        return py_ast.Name(node.id, self.convert_to_python_node(node.ctx))

    def visit_NoneType(self, node):  # coverage: not missing
        return self.NONE_SENTINEL

    def visit_Num(self, node):
        n = node.n
        if isinstance(n, int):
            cls = py_ast.Int
        elif isinstance(n, float):
            cls = py_ast.Float
        elif isinstance(n, complex):
            cls = py_ast.Complex
        # Can't happen, but still there... :)
        else:
            self._log_error("Unknown number type: {}".format(type(n)))
            return None
        return cls(n)
