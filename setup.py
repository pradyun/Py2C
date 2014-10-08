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
    print("Need setuptools to run this script. Please install setuptools.")
    sys.exit(1)

try:
    # If ever setuptools decides to implement a build_py command!
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.command.build_py import build_py as _build_py

#------------------------------------------------------------------------------
# Generating the AST
#------------------------------------------------------------------------------
from os.path import join, realpath


def get_ast_gen():
    """Loads and returns `ast_gen` module.
    """
    sys.path.append(realpath(join(__file__, "..")))
    import ast_gen
    sys.path.pop()

    return ast_gen

path_to_ast_definitions = realpath(join(__file__, "..", "py2c", "syntax_tree"))


class build_py(_build_py):
    """A customized version to build the AST definition files
    """

    def run(self):
        ast_gen = get_ast_gen()
        ast_gen.generate(path_to_ast_definitions, path_to_ast_definitions)
        _build_py.run(self)


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
