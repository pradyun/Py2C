"""Miscellaneous things done multiple times in the package, moved here.
"""

__all__ = [
    "verify_attribute", "get_article", "is_valid_dotted_identifier",
    "get_temp_variable_name"
]


def verify_attribute(obj, name, clazz):
    """Verify that 'obj' has an attribute 'name' which isinstance of 'clazz'.
    """
    if not hasattr(obj, name):
        raise AttributeError("{} should have a {} attribute.".format(
            obj.__class__.__qualname__, name
        ))
    elif not isinstance(getattr(obj, name), clazz):
        raise TypeError(
            "{}.{} should be an instance of a subclass of {!r}".format(
                obj.__class__.__qualname__, name, clazz.__qualname__
            )
        )


# You don't need test coverage for something like this. You can't really mess
# this up, unless you name things with multiple encodings.
# But then it's probably the keyboard that's broken, not the code.
def get_article(type_):  # coverage: not missing
    """Get the appropriate article for type 'type_' in an error message.
    """
    if type_.__name__[0].lower() in "aeiou":
        return "an"
    else:
        return "a"


def is_valid_dotted_identifier(string):
    """Check if the given string is a valid dotted identifier.
    """
    return all(part.isidentifier() for part in string.split("."))

# -----------------------------------------------------------------------------
# Internal variable name related stuff
# -----------------------------------------------------------------------------
_TEMP_NAME_PREFIX = "_PY2C_"

# Prevent over-write on reload or reimport
try:
    _temp_var_dict
except NameError:
    _temp_var_dict = {}


def is_py2c_temp_var(name):
    """Is the passed name a py2c internal variable
    """
    return name.startswith(_TEMP_NAME_PREFIX)


def get_temp_variable_name(name, node=None):
    """Gives a unique variable name for use as an internal variable.

    A node may be for type-specific name assignments.
    """
    key = (type(node), name)

    _temp_var_dict[key] = _temp_var_dict.get(key, 0) + 1
    return "{}{}{}".format(_TEMP_NAME_PREFIX, name, _temp_var_dict[key])
