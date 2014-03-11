#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The module serves as a wrapper to the generated file (_dual_ast.py).
If '_dual_ast.py' doesn't exist, it gets '_ast_gen.py' to generate it from
the specification in '_ast_nodes.cfg' and then imports it.

This way, we guarantee that even if we don't ship the '_dual_ast.py' file,
we generate it for the user on first run.

Note: During testing, just change the ``DEV`` variable to ``True``.
      Then, the module will be rebuilt (and replaced) even if it exists.
"""

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

#-------------------------------------------------------------------------------
# Building the module
#-------------------------------------------------------------------------------
from os.path import join, realpath, dirname, exists
from . import _ast_gen as ast_gen

base_dir = dirname(realpath(__file__))
del realpath, dirname

# Determines if the module should be (re-)generated on import
build = False

# Files to convert into AST definitions
definition_files = ["python.ast", "intermidiate.ast", "C.ast"]

# Build if  or if the file doesn't exist
if not exists(join(base_dir, "dual_ast.py")):
    build = True

if build:
    ast_gen.generate(base_dir, "dual_ast.py", definition_files)


#-------------------------------------------------------------------------------
# Exporting Names
#-------------------------------------------------------------------------------
# The module exists, import it
from . import _dual_ast

# Don't export private names
__all__ = filter(lambda x: not x.startswith("_"), dir(_dual_ast))

# Remove all the declared names from namespace before import!
del (
    exists, join, base_dir, build, definition_files,
    # Imported modules
    _dual_ast, ast_gen
)

# The file will exist by now. Import the stuff!
from ._dual_ast import *
