"""This package contains tests for the basic Py2C modules. \
It also contains the integration tests for Py2C.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from functools import partial
from nose.tools import nottest, assert_in, assert_not_in

import inspect
import warnings
import traceback


#------------------------------------------------------------------------------
# BE VERY CAREFUL HERE. Changes here are capable of breaking all tests...
#------------------------------------------------------------------------------
class _TestMetaClass(type):
    """A metaclass for all tests for convenience in working with code.
    This metaclass:
      - Makes the 1st line of a test method's docstring it's description.
      - Warns when a subclass has test methods but is not named like a test.
    """
    def __new__(meta, name, bases, dic):
        has_tests = False
        for attr, value in dic.items():
            if attr.startswith("test_") and inspect.isfunction(value):
                has_tests = True
                if value.__doc__ is not None:
                    value.description = value.__doc__.splitlines()[0]
        if has_tests and not name.startswith("Test"):
            traceback.print_stack(inspect.currentframe(), 2)
            warnings.warn("Test subclasses' name should start with 'Test'")
        return super(_TestMetaClass, meta).__new__(meta, name, bases, dic)


class Test(object, metaclass=_TestMetaClass):
    """A base class for all tests for py2c
    """

    @nottest
    def yield_tests(self, test_method, args, described=False, prefix=""):
        for test_args in args:
            if described:
                func = partial(test_method, *test_args[1:])
                func.description = prefix + test_args[0]
            else:
                func = partial(test_method, *test_args)
            yield func

    def assert_message_contains(self, error, required_phrases):
        msg = error.args[0]
        for word in required_phrases:
            if word.startswith("!"):
                assert_not_in(word[1:], msg)
            else:
                # print(repr(word), "in", repr(msg))
                assert_in(word, msg)


def runmodule(capture=True):
    """A shorthand for running tests in test modules
    """
    import nose
    env = {
        "NOSE_WITH_HTML_REPORT": "1",
        "NOSE_HTML_OUTPUT_FILE": "/tmp/test-html/index.html",
    }
    if not capture:
        env["NOSE_NOCAPTURE"] = "1"
    return nose.runmodule(env=env)
