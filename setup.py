#!/usr/bin/python3
#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

# pylint:disable=C0103
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install 'setuptools' to run this script.")
    sys.exit(1)

try:
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.command.build_py import build_py as _build_py

#------------------------------------------------------------------------------
# Generating the AST
#------------------------------------------------------------------------------
from os.path import join, dirname, realpath

sys.path.append(realpath(dirname(__file__)))
try:
    import ast_gen
except Exception:
    print("ERROR: Unable to generate required files...")
    print(" ----> Try again after installing PLY.")
    sys.exit(1)
sys.path.pop()

path_to_ast_definitions = realpath(join(dirname(__file__), "py2c", "ast"))


class build_py(_build_py):
    """A customized version to build the AST definition files
    """

    def initialize_options(self):
        ast_gen.generate(path_to_ast_definitions, path_to_ast_definitions)
        # This line also prevents installation on Python 2 (Not intentional, but helpful)
        super().initialize_options()


#------------------------------------------------------------------------------
# Metadata
#------------------------------------------------------------------------------
description = (
    "A translator to translate implicitly statically typed Python code into "
    "(hopefully) human-readable C++ code."
)

long_description = open("README.md").read()

classifiers = [
    "Development Status :: 1 - Planning",
    "Programming Language :: C++",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Compilers",
]

#------------------------------------------------------------------------------
# The main setup call
#------------------------------------------------------------------------------
setup(
    # Package data
    name="py2c",
    version="0.1-dev",
    packages=find_packages(exclude=["dev_tools"]),
    setup_requires=["ply"],
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
