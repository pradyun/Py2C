#!/usr/bin/python3
#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

# pylint:disable=C0103
import sys
if sys.version_info[:2] < (3, 3):
    print("Cannot run on Python versions before Python 3.3")
    sys.exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install 'setuptools' to run this script.")
    sys.exit(1)

#------------------------------------------------------------------------------
# Generating the AST
#------------------------------------------------------------------------------
from os.path import join, dirname, realpath

try:  # If ever setuptools improves on the build_py command.
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.command.build_py import build_py as _build_py

sys.path.append(realpath(dirname(__file__)))

try:
    import ast_gen
except ImportError as err:
    print("ERROR: ", err)
    print(" ----> Try again after installing PLY.")
    sys.exit(1)
finally:
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
    packages=find_packages(),
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
