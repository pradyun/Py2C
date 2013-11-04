#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The module serves as a wrapper to the generated file ().
If '_dual_ast.py' doesn't exist, it gets '_ast_gen.py' to generate it from
the specification in '_ast_nodes.cfg' and then imports it.

This way, we guarantee that even if we don't ship the '_dual_ast.py' file,
we generate it for the user on first run.

Note: For development, just change the ``DEV`` variable to ``True``.
      Then, the module will be rebuilt (and replaced) even if it exists.
"""
from . import _ast_gen as ast_gen

from os.path import join, realpath, dirname, exists

FNAME = join(dirname(realpath(__file__)), "_dual_ast.py")
# If true, the module will be rebuilt (and replaced) even if it exists.
BUILD = True

def generate_module():
    with open(FNAME, "w") as f:
        f.truncate()
        ast_gen.generate(f)

# Build if the file doesn't exist
if not BUILD and not exists(FNAME):
    BUILD = True
if BUILD:
    generate_module()

# The module exists, import it
from . import _dual_ast

# Don't export private names
__all__ = filter(lambda x: not x.startswith("_"), dir(_dual_ast))

# Remove all the declared names from namespace before import!
del (BUILD, FNAME, join, realpath, dirname, exists, generate_module, _dual_ast, ast_gen)

# The file should exist by now. Import the stuff!
from ._dual_ast import *
