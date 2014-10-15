#!/usr/bin/python3
#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import inspect
from nose.tools import nottest, assert_in, assert_not_in

#------------------------------------------------------------------------------
# BE VERY CAREFUL IN HERE. Changes here are capable of breaking all tests...
#------------------------------------------------------------------------------


class _TestMetaClass(type):
    """A metaclass that make the 1st line of a mothod's docstring it's description.
    """
    # This metaclass doesn't have automated tests
    def __new__(meta, name, bases, dic):
        for attr, value in dic.items():
            if attr.startswith("test_") and inspect.isfunction(value):
                if value.__doc__ is not None:
                    value.description = value.__doc__.splitlines()[0]
        return super(_TestMetaClass, meta).__new__(meta, name, bases, dic)


class Test(object, metaclass=_TestMetaClass):
    """A base class for all tests for py2c
    """

    @nottest
    def yield_tests(self, test_method, args):
        for test_args in args:
            yield tuple([test_method] + list(test_args))

    def check_error_msg(self, error, required_phrases):
        msg = error.args[0]
        for word in required_phrases:
            if word.startswith("!"):
                assert_not_in(word[1:], msg)
            else:
                print(repr(word), "in", repr(msg))
                assert_in(word, msg)


def runmodule():
    """A shorthand for running tests in test modules
    """
    import nose
    return nose.runmodule(env={
        "NOSE_WITH_HTML_REPORT": "1",
        "NOSE_HTML_OUTPUT_FILE": "/tmp/test-html/index.html"
    })
