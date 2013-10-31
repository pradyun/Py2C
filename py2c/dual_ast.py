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
from os.path import join, realpath, dirname, exists

FNAME = join(dirname(realpath(__file__)), "_dual_ast.py")
DEV = False

def generate_module():
    from . import _ast_gen as ast_gen

    with open(FNAME, "w") as f:
        f.truncate()
        ast_gen.generate(f)
    if not DEV:
        print("Generated '_dual_ast.py'")

if DEV:
    generate_module()
else:
    if not exists(FNAME):
        generate_module()

from . import _dual_ast
# don't export private names
__all__ = filter(lambda x: not x.startswith("_"), dir(_dual_ast))

# Remove all the declared names from namespace before import!
del DEV, FNAME, join, realpath, dirname, exists, generate_module, _dual_ast

# The file should exist by now.
from ._dual_ast import *
