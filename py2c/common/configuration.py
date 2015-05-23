"""Configuration handler for the program
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

from py2c.utils import is_valid_dotted_identifier

__all__ = [
    "OptionError", "InvalidOptionError", "NoSuchOptionError",
    "Configuration"
]


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class OptionError(Exception):
    pass


class InvalidOptionError(OptionError):
    pass


class NoSuchOptionError(OptionError):

    def __init__(self, name):
        super().__init__()
        self.name = name


# -----------------------------------------------------------------------------
# Configuration class
# -----------------------------------------------------------------------------
class Configuration(object):
    """Holds all options used throughout the program.
    """

    def __init__(self):
        super().__init__()

        self._options = {}
        self._defaults = {}

        self._valid_options = []

    def register_option(self, option_name, default=None):
        """Register `option_name` as a valid option.
        """
        if not isinstance(option_name, str):
            raise InvalidOptionError(
                "Cannot set a non-string as an option's name."
            )
        if not is_valid_dotted_identifier(option_name):
            raise InvalidOptionError(
                "An option's name should be a valid dotted name."
            )

        self._valid_options.append(option_name)
        self._defaults[option_name] = self._options[option_name] = default

    def set_option(self, option_name, value):
        # Check keys
        if option_name not in self._valid_options:
            raise NoSuchOptionError(option_name)
        # Set value
        self._options[option_name] = value

    def get_option(self, option_name):
        try:
            return self._options[option_name]
        except KeyError:
            raise NoSuchOptionError(option_name)

    def reset(self):
        self._options = self._defaults.copy()
