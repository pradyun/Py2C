#!/usr/bin/python3
"""Holds all Python files containing AST definitions for use in translation
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

#pylint:disable=C0103
import re


#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class ASTError(Exception):
    """Base class of all exceptions raised by this module
    """


class WrongTypeError(ASTError, TypeError):
    """Raised when the value of a field does not fit with the field's type
    """


class FieldError(ASTError, AttributeError):
    """Raised when there is a problem related to fields
    """


class WrongAttributeValueError(FieldError):
    """Raised when the value of a field does not fit with the field's definition
    """


#-------------------------------------------------------------------------------
# Helper
#-------------------------------------------------------------------------------
def iter_fields(node):
    for name, _, _ in node._fields:
        try:
            yield name, getattr(node, name)
        except AttributeError:
            pass


#-------------------------------------------------------------------------------
# identifier object
#-------------------------------------------------------------------------------
class _IdentifierMetaClass(type):

    def __instancecheck__(self, obj):
        return isinstance(obj, str) and self._regex.match(obj) is not None

    def __subclasscheck__(self, obj):
        return issubclass(obj, str)


class _Identifier(str, metaclass=_IdentifierMetaClass):
    """Names of identifiers
    """
    _regex = re.compile("^[a-zA-Z][a-zA-Z0-9_]*$")

    def __init__(self, s):
        super(_Identifier, self).__init__()
        if self._regex.match(s) is None:
            raise WrongAttributeValueError(
                "Invalid value for identifier: {}".format(s)
            )
        else:
            self = s

identifier = _Identifier
identifier.__name__ = identifier.__name__.replace("_Identifier", "identifier")
identifier.__qualname__ = identifier.__qualname__.replace(
    "_Identifier", "identifier"
)

#-------------------------------------------------------------------------------
# Modifiers
#-------------------------------------------------------------------------------
NEEDED, OPTIONAL, ZERO_OR_MORE, ONE_OR_MORE = range(1, 5)


#===============================================================================
# AST base node
#===============================================================================
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
                raise WrongTypeError(msg)

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

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                "{}={!r}".format(a, b) for a, b in iter_fields(self)
            )
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
        raise FieldError("{} has no field {!r}".format(
            self.__class__.__name__, name
        ))

    def _validate_field_value(self, field, value):
        """Check if 'value' is valid to assign to field

        Raises:
            WrongTypeError if not a valid value
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
            WrongTypeError if not a valid value
        """
        if not isinstance(value, type_):
            raise WrongTypeError(
                (
                    "Expected {0} {1} for attribute {2}.{3}, "
                    "got {4!r} which is not {0} {1}"
                ).format(
                    "an" if type_.__name__[0] in "aeiou" else "a",
                    type_.__name__, self.__class__.__name__, name, value
                )
            )

    def _validate_list(self, name, value, type_, min_len):
        """Checks if a list is a valid one for assigning.

        Raises:
            WrongTypeError if not a valid list.
        """
        # 'DRY'ing the code.
        msg = (
            "{} attribute of {} should be a list or tuple containing {} or "
            "more items of type {}"
        ).format(name, self.__class__.__name__, min_len, type_.__name__)

        if not isinstance(value, (list, tuple)) or len(value) < min_len:
            raise WrongTypeError(msg)

        for idx, elem in enumerate(value):
            if not isinstance(elem, type_):
                raise WrongTypeError(
                    msg + ": Wrong type of element {}".format(idx)
                )
