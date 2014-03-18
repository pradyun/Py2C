#!/usr/bin/python3
"""Generate C code
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


from py2c.syntax_tree import iter_fields, nodes


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
        """Resets all attributes of the CodeGenerator before parsing
        """
        self.errors = []

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
        raise CodeGenerationError()

    # Providing output
    def get_code(self, node):
        """Get code from Py2C AST node: `node`

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
        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, nodes.AST):
                        self.visit(item)
            elif isinstance(value, nodes.AST):
                self.visit(value)
