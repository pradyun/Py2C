#!/usr/bin/python
"""The module serves as a wrapper to the generated file (_dual_ast.py).
If '_dual_ast.py' doesn't exist, it gets '_ast_gen.py' to generate it from
the specification in '_ast_nodes.cfg' and then imports it.

This way, we guarantee that even if we don't ship the '_dual_ast.py' file,
we generate it for the user on first run.

Note: During testing, just change the ``DEV`` variable to ``True``.
      Then, the module will be rebuilt (and replaced) even if it exists.
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

#-------------------------------------------------------------------------------
# Building the module
#-------------------------------------------------------------------------------
from os.path import join, realpath, dirname, exists
from py2c import _ast_gen as ast_gen

# Files to convert into AST definitions.
definition_files = [
    "python.ast",
    # "intermidiate.ast",
    # "C.ast"
]

# To decide (behaviour/design):
#  - Move declaration files to a seperate directory? What name?
#  - Write a file instead of dynamically generating the classes?

src = ast_gen.generate(dirname(realpath(__file__)), definition_files)

# Remove all the declared names from namespace before execution!
del (
    exists, dirname, realpath, join, definition_files, ast_gen
)

#E Execute the generated module here!
exec(src)
del src
