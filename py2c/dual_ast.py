#!/usr/bin/python3
"""Provides the AST system according to the declaration files
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
