"""Miscellaneous stuff used in the package
"""


# Taken from six 1.5.2, Used to be compatible with Py2 and Py3
def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass.
    """
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper
