"""Utilities that are useful for modifiers.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

# Used for keeping track of how many variables for a given hint have been used.
VARIABLE_HINT_COUNT = {}


def new_var(hint="tmp"):
    VARIABLE_HINT_COUNT[hint] = VARIABLE_HINT_COUNT.get(hint, 0) + 1
    return "__py2c_{}_{}__".format(hint, VARIABLE_HINT_COUNT[hint])
