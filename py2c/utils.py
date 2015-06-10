"""Miscellaneous things done multiple times in the package, moved here.
(Implementation detail)
"""

__all__ = ["verify_attribute", "get_article", "is_valid_dotted_identifier"]


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
