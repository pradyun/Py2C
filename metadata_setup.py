#!/usr/bin/python3
"""Read options from [metadata] section from setup.cfg
"""

from os.path import dirname, abspath, join
from configparser import ConfigParser

THIS_FILE = __file__


def get_metadata():
    """Read the [metadata] section of setup.cfg and return it as a dict.
    """
    parser = ConfigParser()
    parser.read(_get_cfg_fname())
    options = dict(parser.items("metadata"))
    # return options
    return _normalize(options)


def _get_cfg_fname():
    return join(dirname(abspath(THIS_FILE)), "setup.cfg")


def _normalize(options):
    """Return correct kwargs for setup() from provided options-dict.
    """
    retval = {
        key.replace("-", "_"): value for key, value in options.items()
    }

    # Classifiers
    value = retval.pop("classifiers", None)
    if value and isinstance(value, str):
        classifiers = value.splitlines()
        while "" in classifiers:
            classifiers.remove("")
        retval["classifiers"] = classifiers

    # Long description from file
    description_file = retval.pop("long_description_file", None)
    if description_file:
        with open(description_file) as fdesc:
            retval["long_description"] = fdesc.read()

    return retval
