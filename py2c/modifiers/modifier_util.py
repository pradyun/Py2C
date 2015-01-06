"""Utilities that are useful for modifiers.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------


def reset():
    global VARIABLE_HINT_COUNT
    # Used for keeping track of how many variables for a given hint have been used.
    VARIABLE_HINT_COUNT = {}


def new_var(hint="tmp"):  # coverage: no missing
    """Generate a unique name and return it.
    """
    VARIABLE_HINT_COUNT[hint] = VARIABLE_HINT_COUNT.get(hint, 0) + 1
    return "__py2c_{}_{}__".format(hint, VARIABLE_HINT_COUNT[hint])

# Define the global variables
reset()
