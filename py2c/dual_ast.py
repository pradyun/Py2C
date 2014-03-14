#!/usr/bin/python3
"""Provides the AST system according to the declaration files
"""

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

import re

#pylint:disable=C0103
NEEDED, OPTIONAL, ZERO_OR_MORE, ONE_OR_MORE = range(1, 5)


def identifier(s):
    if re.match("^[a-z][a-zA-Z0-9_]*$", s) is None:
        raise ValueError("Invalid value for identifier: {}".format(s))
    else:
        return str(s)


class AST(object):
    """The base class of all nodes defined in the declarations
    """
    _fields = []

    def __init__(self, *args, **kwargs):
        # A Python equivalent of what is done in _ast.AST.__init__
        # See Python/Python-ast.c:ast_type_init in CPython's sources
        # Added type-checking for type-safety
        super(AST, self).__init__()
        num_fields = len(self._fields)

        if args:
            if len(args) != num_fields:
                msg = "{} constructor takes {}{} positional argument{}".format(
                    self.__class__.__name__,
                    "" if num_fields == 0 else "either 0 or ",
                    num_fields,
                    "" if num_fields == 1 else "s"
                )
                raise TypeError(msg)

            for field, value in zip(self._fields, args):
                setattr(self, field[0], value)

        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __setattr__(self, name, value):
        field = self._get_field_by_name(name)
        self._validate_field_value(field, value)
        self.__dict__[name] = value

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        else:
            return all(
                hasattr(other, name) and
                getattr(other, name) == getattr(self, name)
                for name, _, _ in self._fields
            )

    def finalize(self):  # noqa
        """Finalize and check if all atributes exist
        """
        missing = []
        for name, _, modifier in self._fields:
            if not hasattr(self, name):
                if modifier in (NEEDED, ONE_OR_MORE):
                    missing.append(name)
                elif modifier == OPTIONAL:
                    self.__dict__[name] = None
                elif modifier == ZERO_OR_MORE:
                    self.__dict__[name] = ()
                else:
                    raise AttributeError("{} Unknown modifier for {}".format(
                        self.__class__.__name__, name
                    ))
            else:
                if modifier in (ZERO_OR_MORE, ONE_OR_MORE):
                    self.__dict__[name] = tuple(getattr(self, name))
                    for item in getattr(self, name):
                        # call finalize
                        getattr(item, "finalize", lambda: None)()
                else:
                    # call finalize
                    getattr(getattr(self, name), "finalize", lambda: None)()

        if missing:
            raise AttributeError(
                "{} is missing the required attributes: {}".format(
                    self.__class__.__name__, ", ".join(missing)
                )
            )

    def _get_field_by_name(self, name):
        """Return the field by name
        """
        for field in self._fields:
            if field[0] == name:
                return field
        raise AttributeError("{} has no field {!r}".format(
            self.__class__.__name__, name
        ))

    def _validate_field_value(self, field, value):
        """Check if 'value' is valid to assign to field

        Raises:
            TypeError if not a valid value
        """
        name, type_, modifier = field
        # Validation
        if modifier in (ONE_OR_MORE, ZERO_OR_MORE):
            self._validate_list(
                name, value, type_, 0 if modifier == ZERO_OR_MORE else 1
            )
        else:
            if modifier == OPTIONAL and value is None:
                return
            self._validate_type(name, type_, value)

    def _validate_type(self, name, type_, value):
        """Checks if value is a valid one for assigning to the 'name' field

        Raises:
            TypeError if not a valid value
        """
        if not isinstance(value, type_):
            raise TypeError("Expected {} for attribute {}.{} got {}".format(
                type_, self.__class__.__name__, name, value.__class__
            ))

    def _validate_list(self, name, value, type_, min_len):
        """Checks if a list is a valid one for assigning.

        Raises:
            TypeError if not a valid list.
        """
        # 'DRY'ing the code.
        msg = (
            "{} attribute of {} should be a list or tuple containing {} or "
            "more items of type {}"
        ).format(name, self.__class__.__name__, min_len, type_.__name__)

        if not isinstance(value, (list, tuple)) or len(value) < min_len:
            raise TypeError(msg)

        for idx, elem in enumerate(value):
            if not isinstance(elem, type_):
                raise TypeError(msg + ": Wrong type of element {}".format(idx))


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

sources = ast_gen.generate(dirname(realpath(__file__)), definition_files)

# Remove all the declared names from namespace before execution!
del (
    exists, dirname, realpath, join, definition_files, ast_gen
)
exec_context = {
    # The all important
    "AST": AST,
    # Modifiers
    "NEEDED": NEEDED,
    "ZERO_OR_MORE": ZERO_OR_MORE,
    "ONE_OR_MORE": ONE_OR_MORE,
    "OPTIONAL": OPTIONAL,
    # Types used internally
    "identifier": identifier,
}
# Execute the generated module here!
exec(sources, exec_context, exec_context)
del sources, exec_context
