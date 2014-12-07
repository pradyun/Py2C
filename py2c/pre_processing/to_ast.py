"""Translates Python code into an AST containing type information
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import ast

from py2c.ast import python

# Serves as a stub when a function needs to return None
NONE_STUB = object()


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


class PythonToAST(object):
    """Translates Python code into Py2C AST
    """

    def __init__(self):
        super().__init__()
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

    def _visit(self, node):
        """Visits a node.
        """
        method = '_visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.convert_to_python_node)
        return visitor(node)

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
            retval = self._visit(node)
            self._handle_errors()
            return retval

    #==========================================================================
    # Helpers
    #==========================================================================
    def _visit_children(self, node):  # coverage: not missing
        """Visit all children of node.
        """
        for field, old_value in ast.iter_fields(node):
            old_value = getattr(node, field, None)
            if isinstance(old_value, list):
                self._visit_list(old_value)
            elif isinstance(old_value, ast.AST):
                new_node = self._visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    if new_node is NONE_STUB:
                        new_node = None
                    setattr(node, field, new_node)
        # print(node)

    def _visit_list(self, original_list):  # coverage: not missing
        # Moved out of '_visit' for readablity
        new_list = []
        for value in original_list:
            # Python AST object
            if isinstance(value, ast.AST):
                value = self._visit(value)
                if value is None:
                    continue
                elif value is NONE_STUB:
                    value = None
                elif hasattr(value, "__iter__"):
                    new_list.extend(value)
                    continue
            new_list.append(value)
        original_list[:] = new_list

    def convert_to_python_node(self, node):
        """Convert ``ast`` node (and children) into ``py2c.ast`` nodes.
        """
        self._visit_children(node)

        node_name = node.__class__.__name__
        py_node = getattr(python, node_name)

        retval = py_node(**dict(ast.iter_fields(node)))
        # retval.finalize()

        return retval

    #==========================================================================
    # Visitors, only for specially handled nodes
    #==========================================================================
    def _visit_Name(self, node):
        # coverage excluded as condition is never True in Python 3.4
        if node.id in ["True", "False", "None"]:  # coverage: no partial
            return python.NameConstant(eval(node.id))  # coverage: not missing

        self._visit_children(node)  # XXX: Check if needed.
        self.names_used.add(node.id)  # Make note that the name has been used.
        return python.Name(node.id, node.ctx)

    def _visit_NoneType(self, node):  # coverage: not missing
        return NONE_STUB

    def _visit_Num(self, node):
        n = node.n
        if isinstance(n, int):
            cls = python.Int
        elif isinstance(n, float):
            cls = python.Float
        elif isinstance(n, complex):
            cls = python.Complex
        # Can't happen, but still there... :)
        else:
            self._log_error("Unknown number type: {}".format(type(n)))
            return None
        return cls(n)
