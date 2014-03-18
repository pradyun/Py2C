"""This package contains helpers for the setup.py script
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

import os
from . import ast_gen
from setuptools.command.build_py import build_py

path_to_ast_package = os.path.realpath(
    os.path.join(__file__, "..", "..", "py2c", "ast")
)


class BuildPyCommand(build_py):
    """A customized version to build the AST definition files
    """
    def run(self):
        ast_gen.generate(path_to_ast_package, path_to_ast_package)
        build_py.run(self)
