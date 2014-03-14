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

import sys
from setuptools import setup, find_packages

# pylint:disable=C0103
description = (
    "A translator to translate implicitly statically typed Python code into "
    "(hopefully) human-readable C++ code."
)

long_description = open("README.md").read()

# Metadata
classifiers = [
    "Development Status :: 1 - Planning",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Compilers",
]

# For running tests
tests_require = ["nose"]
if sys.version_info[:2] < (3, 3):
    tests_require.extend([
        "mock",
    ])

# The main setup call
setup(
    # Package data
    name="py2c",
    version="0.1-dev",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "py2c": ["*.ast"],  # include the declaration files
    },
    install_requires=["ply"],
    zip_safe=False,
    # Metadata
    description=description,
    long_description=long_description,
    author="Pradyun S. Gedam",
    author_email="pradyunsg@gmail.com",
    url="https://github.com/pradyun/Py2C",
    classifiers=classifiers,
    # Testing
    extras_require={
        "nosetests": tests_require,
    },
)
