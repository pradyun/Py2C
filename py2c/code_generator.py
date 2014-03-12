#!/usr/bin/python
"""
"""

# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from . import dual_ast


class CodeGenerationError(Exception):
    """Raised when there is an error during translation
    """


class CodeGenerator(object):
    """Converts AST into C source code
    """

    def __init__(self):
        super(CodeGenerator, self).__init__()
        self.reset()

    #---------------------------------------------------------------------------
    # API
    #---------------------------------------------------------------------------
    # Errors
    def reset(self):
        self.errors = []

    def log_error(self, msg, lineno=None):
        if lineno is not None:
            msg += "Check Line ({0}): {1}".format(lineno, msg)
        self.errors.append(msg)

    def handle_errors(self):
        if not self.errors:
            return
        raise CodeGenerationError()

    # Providing output
    def get_code(self, node):
        """Get code from dual AST node: `node`

        Args:
            node: The AST to be converted to code
        Returns:
            A string containing the code
        Raises:
            CodeGenerationError when there is any error during CodeGeneration
        """
        self.reset()
        retval = self.visit(node)
        self.handle_errors()
        return retval

    #---------------------------------------------------------------------------
    # Code Generation API, like ast.NodeVisitor
    #---------------------------------------------------------------------------
    def visit(self, node):
        """Visit a node.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node.
        """
        for field, value in dual_ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dual_ast.AST):
                        self.visit(item)
            elif isinstance(value, dual_ast.AST):
                self.visit(value)
