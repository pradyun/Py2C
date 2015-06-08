"""The internal representation of the Python code-flow.
"""

import collections

from py2c.utils import (
    get_article, verify_attribute
)

__all__ = [
    # Exceptions
    "NodeError", "WrongTypeError", "FieldError", "WrongAttributeValueError",
    # Custom classes
    "identifier",
    # A field access related helper
    "fields_decorator",
    # The big fish
    "Node"
]


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class NodeError(Exception):
    """Base class of all exceptions raised by this module
    """


class WrongTypeError(NodeError, TypeError):
    """Raised when the value of a field does not fit with the field's type
    """


class InvalidInitializationError(NodeError, TypeError):
    """Raised when the value of a field does not fit with the field's type
    """


class FieldError(NodeError, AttributeError):
    """Raised when there is a problem related to fields
    """


class WrongAttributeValueError(FieldError):
    """Raised when the value of a field does not match the field's definition.
    """


# -----------------------------------------------------------------------------
# Helper
# -----------------------------------------------------------------------------
def iter_fields(node):
    for name, _, _ in node._fields:
        try:
            yield name, getattr(node, name)
        except AttributeError:
            pass


# -----------------------------------------------------------------------------
# identifier object
# -----------------------------------------------------------------------------
class _IdentifierMetaClass(type):
    def __instancecheck__(self, obj):
        return isinstance(obj, str) and obj.isidentifier()

    def __subclasscheck__(self, obj):
        return issubclass(obj, str)


class identifier(str, metaclass=_IdentifierMetaClass):
    def __new__(self, obj):
        if isinstance(obj, str) and obj.isidentifier():
            return obj
        raise WrongAttributeValueError(
            "Invalid value for identifier: {}".format(obj)
        )


# -----------------------------------------------------------------------------
# Allow for delayed attribute loading in generated attribute's fields, by
# creating class level properties
# -----------------------------------------------------------------------------
class class_property(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def fields_decorator(func):
    return class_property(classmethod(func))


# -----------------------------------------------------------------------------
# Refactored out the error messages, as they create noise in the implemetation.
# -----------------------------------------------------------------------------
def _invalid_arg_count_err_msg(node):
    # Complicated thanks to English..
    num_fields = len(node._fields)
    msg = node.__class__.__name__ + " constructor takes "
    if num_fields != 0:
        msg += "either 0 or"
    else:
        msg += "no"
    msg += " " + str(num_fields) + " positional argument"
    if num_fields != 1:  # TODO:: Refactor out.
        msg += "s"
    return msg


def _missing_fields_err_msg(node, missing):
    return "{} is missing {}".format(
        node.__class__.__name__, ", ".join(missing)
    )


def _invalid_modifiers_err_msg(node, invalid_modifiers):
    return "{0}'s field{2} used invalid modifier{2}: {1}".format(
        node.__class__.__name__,
        ", ".join(
            "{} -> '{}'".format(name, modifier)
            for name, modifier in invalid_modifiers
        ),
        "s" if len(invalid_modifiers) != 1 else ""  # TODO:: Refactor out.
    )


def _no_field_by_name_err_msg(node, name):
    return "{} has no field {!r}".format(node.__class__.__name__, name)


def _invalid_field_value_type_err_msg(node, name, type_, value):
    return (
        "Expected {0} {1} for attribute {2}.{3}, got {4!r} which is not {0} "
        "{1}"
    ).format(
        get_article(type_), type_.__name__, node.__class__.__name__, name,
        value
    )


def _invalid_iterable_field_value_err_msg(node, name, min_len, type_, index=None, elem=None):  # noqa
    msg = (
        "{}.{} should be an sequence containing {} or more items of type {}"
    ).format(
        node.__class__.__name__, name, min_len, type_.__name__
    )

    if index is not None:
        msg += "\nWrong type of element {}: {!r}".format(index, elem)
    return msg


# =============================================================================
# Node base node
# =============================================================================
class Node(object):
    """The base class of all nodes defined in the declarations
    """
    _special_names = []

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__()
        verify_attribute(self, "_fields", collections.Iterable)

        self.check_modifiers()

        if len(args) not in [0, len(self._fields)]:
            raise InvalidInitializationError(_invalid_arg_count_err_msg(self))

        # Setup from arguments
        for field, value in zip(self._fields, args):
            setattr(self, field[0], value)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        else:
            stub = object()
            return all(
                getattr(other, name, stub) == getattr(self, name, stub)
                for name, _, _ in self._fields
            )

    def __repr__(self):
        # Should this be changed into a loop and list.append?
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(
                "{}={!r}".format(a, b) for a, b in iter_fields(self)
            )
        )

    def __setattr__(self, name, value):
        # Special names don't pass through the field-related filters
        if name in self._special_names:  # coverage: not missing
            super().__setattr__(name, value)

        for field in self._fields:
            if name == field[0]:
                self._validate_value_for_field(field, value)
                self._set_field_value(name, value)
                break
        else:
            raise FieldError(_no_field_by_name_err_msg(self, name))

    def check_modifiers(self):
        """Check the modifiers of the Node's fields.
        """
        invalid_modifiers = []
        for name, type_, modifier in self._fields:
            if modifier not in ['NEEDED', 'OPTIONAL', 'ZERO_OR_MORE', 'ONE_OR_MORE']:  # noqa
                invalid_modifiers.append((name, modifier))
        if invalid_modifiers:
            raise InvalidInitializationError(
                _invalid_modifiers_err_msg(self, invalid_modifiers)
            )

    def finalize(self):  # noqa
        """Finalize and check if all attributes exist
        """
        missing = []
        for name, _, modifier in self._fields:
            if hasattr(self, name):
                if modifier in ('ZERO_OR_MORE', 'ONE_OR_MORE'):
                    # Not nice, but used for brevity, probably a bad idea...
                    items = tuple(getattr(self, name))
                    self._set_field_value(name, items)
                elif modifier in ('NEEDED', 'OPTIONAL'):
                    items = [getattr(self, name)]
                else:
                    assert False, "Should not have reached this branch!!"

                for item in filter(lambda x: isinstance(x, Node), items):
                    item.finalize()
            # Attribute missing!
            elif modifier in ('NEEDED', 'ONE_OR_MORE'):
                missing.append(name)
            elif modifier == 'OPTIONAL':
                self.__dict__[name] = None
            elif modifier == 'ZERO_OR_MORE':
                self.__dict__[name] = ()
            else:
                assert False, "Should not have reached this branch!!"

        if missing:
            raise AttributeError(_missing_fields_err_msg(self, missing))

    def _validate_value_for_field(self, field, value):
        """Check if 'value' is valid to assign to field
        """
        name, type_, modifier = field
        # Validation
        if modifier in ('ONE_OR_MORE', 'ZERO_OR_MORE'):
            self._validate_field_list(
                name, value, type_, 0 if modifier == 'ZERO_OR_MORE' else 1
            )
        else:
            if modifier == 'OPTIONAL' and value is None:
                return
            self._validate_type(name, type_, value)

    def _validate_type(self, name, type_, value):
        """Checks if value is a valid one for assigning to the 'name' field

        Raises:
            WrongTypeError if not a valid value
        """
        if not isinstance(value, type_):
            raise WrongTypeError(_invalid_field_value_type_err_msg(
                self, name, type_, value
            ))

    def _validate_field_list(self, name, value, type_, min_len):
        """Checks if a list is a valid one for assigning.

        Raises:
            WrongTypeError if not a valid list.
        """
        if not isinstance(value, (list, tuple)) or len(value) < min_len:
            raise WrongTypeError(_invalid_iterable_field_value_err_msg(
                self, name, min_len, type_
            ))

        for index, elem in enumerate(value):
            if not isinstance(elem, type_):
                raise WrongTypeError(_invalid_iterable_field_value_err_msg(
                    self, name, min_len, type_, index, elem
                ))

    def _set_field_value(self, name, value):
        self.__dict__[name] = value

    # Make sure sub-classes don't use this.
    @property
    def _fields(self):
        raise InvalidInitializationError(
            "Node sub-classes need to define an iterable _fields attribute."
        )
