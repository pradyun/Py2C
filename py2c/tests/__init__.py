"""Test-related helpers
"""

import inspect
import warnings
import traceback
from functools import partial, wraps

from unittest import mock
from nose.tools import istest, nottest, assert_in, assert_not_in

__all__ = ["Test", "mock", "runmodule"]

# =============================================================================
# BE VERY CAREFUL HERE. Changes here are capable of breaking all tests...
# =============================================================================

# MARK:: Bad!!! We monkey-patch spec to show nice-output.
try:
    import spec.plugin
except ImportError:
    pass
else:
    if not hasattr(spec.plugin, "_py2c_monkey_patched"):
        def noseMethodDescription(test):
            return (
                (hasattr(test.test, "description") and test.test.description)
                or test.method.__doc__
                or spec.plugin.underscored2spec(test.method.__name__)
            )
        spec.plugin.noseMethodDescription = noseMethodDescription
        spec.plugin._py2c_monkey_patched = True

        del noseMethodDescription


# -----------------------------------------------------------------------------
# Base-class for all Test classes.
# -----------------------------------------------------------------------------
class Test(object):
    """Base class for all tests for py2c

    This base-class:
      - Makes the 1st line of a test method's docstring it's description.
      - Warns when a subclass has test methods but is not named like a test.
    """

    def __init__(self):
        has_tests = False
        for attr, value in self.__dict__.items():
            if attr.startswith("test_") and inspect.isfunction(value):
                has_tests = True
                if value.__doc__ is not None:
                    value.description = value.__doc__.splitlines()[0]
            elif attr.startswith("Test"):
                has_tests = True
                print(attr)
        if has_tests and not self.__name__.startswith("Test"):
            traceback.print_stack(inspect.currentframe(), 2)
            warnings.warn("Test subclasses' name should start with 'Test'")
        super().__init__()

    def assert_error_message_contains(self, error, required_phrases):
        msg = error.args[0]
        for word in required_phrases:
            if word.startswith("!"):
                assert_not_in(word[1:], msg)
            else:
                assert_in(word, msg)

    def fail(self, message="", cause=None):
        """Fail a test for whatever reason.

        Because `fail(...)` looks better than `assert False, ...`
        """
        raise AssertionError(message) from cause


# -----------------------------------------------------------------------------
# Data Driven Tests
# -----------------------------------------------------------------------------
@nottest
def data_driven_test(data, described=False, prefix="", suffix=""):
    """Run a test for all the provided data

    Usage::

        data = [['1'], ['2']]
        @data_driven(data)
        def decorated(*args):
            print(args)

        for func in decorated():
            func()

    """

    def decorator(function):
        @istest  # MARK:: Should this be here?
        @wraps(function)
        def wrapped(*args):
            nonlocal data, described, prefix, suffix
            for test_data in data:
                if described:
                    func = partial(function, *(list(args) + list(test_data)[1:]))  # noqa
                    func.description = prefix + test_data[0] + suffix
                else:
                    func = partial(function, *(list(args) + list(test_data)))
                print(func)
                yield func
        return wrapped

    return decorator


# -----------------------------------------------------------------------------
# Running tests directly from a module
# -----------------------------------------------------------------------------
def runmodule(capture=True):
    """A convenience function for running tests in test modules
    """
    import os
    import nose

    env = {
        "NOSE_WITH_HTML_REPORT": "True",
        "NOSE_HTML_OUTPUT_FILE": "/tmp/test-html/index.html",
        "NOSE_WITH_SPECPLUGIN": "True"
    }
    if not capture:
        env["NOSE_NOCAPTURE"] = "1"
    env.update(os.environ)
    return nose.runmodule(env=env)
