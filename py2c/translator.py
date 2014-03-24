#!/usr/bin/python3
"""Translates Python code into an AST containing type information
"""

#-------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------


import ast
import __future__ as future
from py2c.syntax_tree import python

# Serves as a stub when a function needs to return None
NONE_STUB = object()


#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class TranslationError(Exception):
    """Raised when a fatal error occurs in Translation
    """
    def __init__(self, msg="", errors=None):
        super(TranslationError, self).__init__()
        self.msg = msg
        self.errors = errors


# Although it is like a NodeTransformer, it doesn't need to be inherit
# from it as we define our own custom versions of those functions
# NodeTrasnsformer implements in itself.
class Python2ASTTranslator(object):
    """Translates Python code into Py2C AST

    This is a NodeTrasnsformer that visits the Python AST validates it for
    conversion and creates another AST with space for type definitions and other
    stuff, from which code can be generated.
    """

    def __init__(self):
        super(Python2ASTTranslator, self).__init__()
        self._reset()

    def _reset(self):
        """Resets all attributes of the CodeGenerator before parsing
        """
        self.errors = []

    #===========================================================================
    # External API
    #===========================================================================
    # Errors
    def log_error(self, msg, lineno=None):
        """Log an error in the provided code
        """
        if lineno is not None:
            msg += "Check Line ({0}): {1}".format(lineno, msg)
        self.errors.append(msg)

    def handle_errors(self):
        """Handle the errors, if any, logged during generation
        """
        if not self.errors:
            return
        raise TranslationError(errors=self.errors)

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
            raise TranslationError("Unable to generate AST from Python code")
        else:
            # print("AST:    ", ast.dump(node))
            retval = self.visit(node)
            # self.handle_errors()
            return retval

    # Modified: Uses ``syntax_tree`` nodes instead of ``ast`` nodes accordingly.
    def generic_visit(self, node):
        """
        """
        for field, old_value in ast.iter_fields(node):
            old_value = getattr(node, field, None)
            if isinstance(old_value, list):
                self.visit_list(old_value)
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    if new_node is NONE_STUB:
                        new_node = None
                    setattr(node, field, new_node)
        # print(node)

    def visit(self, node):
        """Visit a node.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.convert_to_python_node)
        return visitor(node)

    #===========================================================================
    # Helpers
    #===========================================================================
    def add_types(self, target, right):
        """Add the types in right to target, recursively.
        """
        if isinstance(target, python.AST) and hasattr(target, "types"):
            if isinstance(right, python.Name):
                target.types.update(right.types)
            elif right.__class__ in self.type_map:
                target.types.add(self.types[right.__class__])
            else:
                # TODO: FIx this!
                raise NotImplementedError("Can't handle non-literals yet.")

        elif hasattr(target, "__iter__"):
            for elem in target:
                self.add_types(elem, right)

    def visit_list(self, old):
        new_list = []
        for value in old:
            # Python AST object
            if isinstance(value, ast.AST):
                value = self.visit(value)
                if value is None:
                    continue
                elif value is NONE_STUB:
                    value = None
                elif hasattr(value, "__iter__"):
                    new_list.extend(value)
                    continue
            new_list.append(value)
        old[:] = new_list

    def visit_children(func):
        def wrapper(self, node):
            self.generic_visit(node)
            return func(self, node)
        return wrapper

    def finalize(func):
        def wrapper(self, node):
            retval = func(self, node)
            if retval is not None:
                retval.finalize()
            return retval
        return wrapper

    def convert_to_python_node(self, node):
        """Convert ``ast`` node and its children into ``py2c.syntax_tree`` nodes
        """
        self.generic_visit(node)

        node_name = node.__class__.__name__
        py_node = getattr(python, node_name)

        retval = py_node(**dict(ast.iter_fields(node)))
        retval.finalize()

        return retval

    #===========================================================================
    # Visitors, only for specially handled nodes
    #===========================================================================
    def visit_NoneType(self, node):
        return NONE_STUB

    @finalize
    def visit_Num(self, node):
        n = node.n
        if isinstance(n, int):
            cls = python.Int
        elif isinstance(n, float):
            cls = python.Float
        elif isinstance(n, complex):
            cls = python.Complex
        else:
            self.log_error("Unknown number type: {}".format(type(n)))
        return cls(n)

    # Statements
    @finalize
    @visit_children
    def visit_Assign(self, node):
        self.add_types(node.targets, node.value)
        return python.Assign(node.targets, node.value)

    @finalize
    @visit_children
    def visit_ImportFrom(self, node):
        # We handle Future imports specially, although they do nothing in Py3!
        # Just incase we want to support Python 2!
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
    with some_context as some_name:
        pass
    """
    print("    AST:", ast.dump(ast.parse(dedent(s))))
    translator = Python2ASTTranslator()
    print("Returns:", end=" ")
    # print(translator.convert_to_python_node(ast.parse(s)))
    print(translator.get_node(dedent(s)))
