"""Test-related helpers
"""

import inspect
import warnings
import traceback
from os.path import abspath, join, dirname
from functools import partial, wraps


import yaml
from unittest import mock
from nose.tools import nottest, assert_in, assert_not_in

__all__ = ["Test", "mock", "runmodule", "data_driven_test"]

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
#    Implements extras for checking names of tests, adding descriptions from
#    docstring and (BIG) loading from string, sourced from YAML files.
# -----------------------------------------------------------------------------
class Test(object):
    """Base class for all tests for py2c

    This base-class:
      - Makes the 1st line of a test method's docstring it's description.
      - Warns when a subclass has test methods but is not named like a test.
    """

    context = None

    def __init__(self):
        super().__init__()

        # Process test functions
        for attr, value in self.__dict__.items():
            if attr.startswith("test_") and inspect.isfunction(value):
                self._process_test_function(attr, value)

        # Check name
        has_tests = any(key.lower().startswith("test") for key in self.__dict__)
        if has_tests and not self.__name__.startswith("Test"):
            traceback.print_stack(inspect.currentframe(), 2)
            warnings.warn("Test subclasses' name should start with 'Test'")

    def _process_test_function(self, name, function):
        # Set a description if not already set, using the doc-string if it's there
        if not (function.__doc__ is None or hasattr(function, "description")):
            function.description = function.__doc__.splitlines()[0]

    def assert_error_message_contains(self, error, required_phrases):
        """Assert the error message contains/does not contain the phrases
        """
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

    # Helpers for data-driven testing
    def load(self, value, context=None):
        """Load data in given context
        """
        # NOTE:: Folks at python-ideas are working on a nicer version for this...
        #        Keep track.
        if context is None:
            context = self.context if self.context is not None else {}

        def _eval(value, context):
            if isinstance(value, str):
                return _eval_str(value, context)
            else:
                return value

        def _eval_str(string, context):
            # Errors should propagate upward
            return eval(string, context, context)

        def _eval_list(li, context):
            for i, elem in enumerate(li.copy()):
                li[i] = _eval(elem, context)
            return li

        def _eval_dict(di, context):
            for key, elem in di.items():
                di[key] = _eval(elem, context)
            return di

        if isinstance(value, list):
            func = _eval_list
        elif isinstance(value, dict):
            func = _eval_dict
        else:
            func = _eval

        return func(value, context)


# -----------------------------------------------------------------------------
# Data Driven Tests
# -----------------------------------------------------------------------------
@nottest
def data_driven_test(test_data_or_file, *, prefix="", suffix=""):
    """Mark a test as a Data-Driven Test
    """

    def decorator(function):

        # Wrapper function
        @wraps(function)
        def wrapper(*passed_args):
            # File-name provided, load test-data from file
            if isinstance(test_data_or_file, str):
                # Put all data in the data directory of file folder
                base_path = dirname(abspath(inspect.getsourcefile(function)))
                data_file_path = join(base_path, "data", test_data_or_file)

                try:
                    with open(data_file_path) as f:
                        data = yaml.load(f)
                except Exception as e:
                    raise RuntimeError("Could not load test-data") from e

            # Test-data provided, use as is
            else:
                data = test_data_or_file

            seen_descriptions = set()

            for di in data:
                description = di.pop("description", None)
                if description in seen_descriptions:
                    warnings.warn("Found repeated description: {!r}".format(description))

                args = di.pop("args", [])
                kwargs = di.pop("kwargs", {})
                if not args and not kwargs:
                    warnings.warn("Got no arguments: {!r}".format(description))

                args = list(passed_args) + list(args)

                val = partial(function, *args, **kwargs)
                if description is not None:
                    val.description = prefix + description + suffix

                seen_descriptions.add(description)
                yield val

        return wrapper
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
