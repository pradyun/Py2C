#!/usr/bin/python3
"""Translates Python code into an AST containing type information
"""

import ast
import __future__ as future
from py2c.syntax_tree import python

# Serves as a stub when a function needs to return None
NONE_STUB = object()


#------------------------------------------------------------------------------
# Exceptions
#------------------------------------------------------------------------------
class TranslationError(Exception):
    """Raised when a fatal error occurs in Translation
    """

    def __init__(self, msg="", errors=None):
        super(TranslationError, self).__init__(msg, errors)
        self.msg = msg
        self.errors = errors


# Although it is like a NodeTransformer, it doesn't inherit from it as we
# define our own custom versions of those functions NodeTransformer implements
# in itself. Plus we need this added stuff too...
class Python2ASTTranslator(object):
    """Translates Python code into Py2C AST

    This is a Node-visitor that visits the Python AST and creates another AST
    with space for type definitions and other stuff, on which further
    processing takes place.
    """

    def __init__(self):
        super(Python2ASTTranslator, self).__init__()
        self._reset()

    def _reset(self):
        """Resets all attributes of the CodeGenerator before parsing
        """
        self.errors = []
        self.names_used = set()

    #==========================================================================
    # External API
    #==========================================================================
    # Errors
    def log_error(self, msg, lineno=None):
        """Log an error in the provided code
        """
        if lineno is not None:
            msg = "Line {0}: {1}".format(lineno, msg)
        self.errors.append(msg)

    def handle_errors(self):
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

    def get_node(self, code):
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
            self.handle_errors()
            return retval

    def generic_visit(self, node):
        """
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

    #==========================================================================
    # Helpers
    #==========================================================================

    def _visit_list(self, old):
        new_list = []
        for value in old:
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
        old[:] = new_list

    def _visit_children(func):
        def wrapper(self, node):
            self.generic_visit(node)
            return func(self, node)
        return wrapper

    # def finalize(func):
    #     def wrapper(self, node):
    #         retval = func(self, node)
    #         # if retval is not None:
    #         #     retval.finalize()
    #         return retval
    #     return wrapper

    def convert_to_python_node(self, node):
        """Convert ``ast`` node (and children) into ``py2c.syntax_tree`` nodes.
        """
        self.generic_visit(node)

        node_name = node.__class__.__name__
        py_node = getattr(python, node_name)

        retval = py_node(**dict(ast.iter_fields(node)))
        # retval.finalize()

        return retval

    #==========================================================================
    # Visitors, only for specially handled nodes
    #==========================================================================
    # Needed in Python < 3.4
    # @finalize
    def _visit_Name(self, node):
        if node.id in ["True", "False", "None"]:  # coverage: no partial
            return python.NameConstant(eval(node.id))  # coverage: not missing
        else:
            self.generic_visit(node)
            self.names_used.add(node.id)
            return python.Name(node.id, node.ctx)

    def _visit_NoneType(self, node):
        return NONE_STUB

    # @finalize
    def _visit_Num(self, node):
        n = node.n
        if isinstance(n, int):
            cls = python.Int
        elif isinstance(n, float):
            cls = python.Float
        elif isinstance(n, complex):
            cls = python.Complex
        # Shouldn't happen, but better safe than sorry!
        else:
            self.log_error("Unknown number type: {}".format(type(n)))
            return None
        return cls(n)

    # @finalize
    @_visit_children
    def _visit_ImportFrom(self, node):
        # We handle Future imports specially, although they do nothing in Py3!
        # Just incase we ever want to support Python 2!
        if node.module is "__future__" and not node.level:
            bail_out = False
            for feature in node.names:
                if not hasattr(future, feature.name):
                    self.log_error(
                        "__future__ has no feature {!r}".format(feature.name)
                    )
                    bail_out = True
            if bail_out:
                return None

            return python.Future(node.names)

        return python.ImportFrom(node.module, node.names, node.level)


if __name__ == '__main__':
    from textwrap import dedent

    s = """
    if a:
        betterc
    """
    print("AST    :", ast.dump(ast.parse(dedent(s))))
    translator = Python2ASTTranslator()
    print("Returns:", end=" ")
    # print(translator.convert_to_python_node(ast.parse(s)))
    print(translator.get_node(dedent(s)))
