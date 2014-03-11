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
