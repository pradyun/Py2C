#!/usr/bin/python3
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
# pylint:disable=C0103

import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Need setuptools to run this script. Please install setuptools.")
    sys.exit(1)

try:
    # If ever setuptools decides to improve the build command!
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.command.build_py import build_py as _build_py

#-------------------------------------------------------------------------------
# Generating the AST
#-------------------------------------------------------------------------------
from os.path import join, realpath
# Importing AST generator
sys.path.append(realpath(join(__file__, "..")))
import ast_gen
sys.path.pop()

path_to_ast_definitions = realpath(join(__file__, "..", "py2c", "syntax_tree"))


class build(_build_py):
    """A customized version to build the AST definition files
    """
    def run(self):
        ast_gen.generate(path_to_ast_definitions, path_to_ast_definitions)
        _build_py.run(self)


#-------------------------------------------------------------------------------
# Metadata
#-------------------------------------------------------------------------------
description = (
    "A translator to translate implicitly statically typed Python code into "
    "(hopefully) human-readable C++ code."
)

long_description = open("README.md").read()

classifiers = [
    "Development Status :: 1 - Planning",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Compilers",
]

#-------------------------------------------------------------------------------
# The main setup call
#-------------------------------------------------------------------------------
setup(
    # Package data
    name="py2c",
    version="0.1-dev",
    packages=find_packages(exclude=["dev_tools"]),
    install_requires=["ply"],
    # Metadata
    description=description,
    long_description=long_description,
    author="Pradyun S. Gedam",
    author_email="pradyunsg@gmail.com",
    url="https://github.com/pradyun/Py2C",
    classifiers=classifiers,
    cmdclass={
        'build_py': build_py,
    },
)
