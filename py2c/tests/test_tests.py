"""Unit-tests for `py2c.tests`
"""

import warnings
from collections.abc import Iterable

from nose.tools import eq_, assert_raises
from py2c.tests import Test, data_driven_test


class TestDataDriven(Test):
    """py2c.tests.data_driven_test
    """

    def _check_descriptions(self, val, func):
        with warnings.catch_warnings(record=True):  # ensure no warnings show in runs
            for i, test in enumerate(val):
                eq_(test.description, func(i))

    def assert_is_an_iterable(self, val):
        assert isinstance(val, Iterable), "{!r} is not an iterable!!".format(val)

    def test_does_not_yield_when_empty_data_is_passed(self):
        data = []

        @data_driven_test(data)
        def func():
            pass

        val = func()
        self.assert_is_an_iterable(val)

        for test in val:
            raise self.failureException("Should not have yielded any values.")

    def test_attaches_correct_descriptions(self):
        data = [
            {"description": "test-1"},
            {"description": "test-2"}
        ]

        @data_driven_test(data)
        def func():
            pass

        val = func()
        self.assert_is_an_iterable(val)
        self._check_descriptions(val, lambda i: "test-" + str(i + 1))

    def test_attaches_prefix_to_descriptions(self):
        data = [
            {"description": "test-1"},
            {"description": "test-2"}
        ]

        @data_driven_test(data, prefix="prefix-")
        def func():
            pass

        val = func()
        self.assert_is_an_iterable(val)
        self._check_descriptions(val, lambda i: "prefix-" + "test-" + str(i + 1))

    def test_attaches_suffix_to_descriptions(self):
        data = [
            {"description": "test-1"},
            {"description": "test-2"}
        ]

        @data_driven_test(data, suffix="-suffix")
        def func():
            pass

        val = func()
        self.assert_is_an_iterable(val)
        self._check_descriptions(val, lambda i: "test-" + str(i + 1) + "-suffix")

    def test_attaches_prefix_and_suffix_to_descriptions(self):
        data = [
            {"description": "test-1"},
            {"description": "test-2"}
        ]

        @data_driven_test(data, prefix="prefix-", suffix="-suffix")
        def func():
            pass

        val = func()
        self.assert_is_an_iterable(val)
        self._check_descriptions(val, lambda i: "prefix-" + "test-" + str(i + 1) + "-suffix")

    def test_warns_on_same_descriptions(self):
        data = [
            {"description": "test-1", "args": [1]},
            {"description": "test-1", "args": [1]}
        ]

        @data_driven_test(data)
        def func(arg):
            eq_(arg, 1)

        val = func()
        self.assert_is_an_iterable(val)

        with warnings.catch_warnings(record=True) as w:
            for test in val:
                eq_("test-1", test.description)

            eq_(len(w), 1, "Did not get expected number of warnings")
            self.assert_error_message_contains(w[0].message, ["repeated"])

    def test_warns_when_no_arguments_passed(self):
        data = [
            {},  # Empty Test
            {"description": "test-2"},  # Test with only description
        ]

        @data_driven_test(data)
        def func():
            pass

        val = func()
        self.assert_is_an_iterable(val)

        with warnings.catch_warnings(record=True) as w:
            for i, test in enumerate(val):
                eq_(len(w), i+1, "Did not get expected number of warnings")
                self.assert_error_message_contains(w[-1].message, ["no", "arguments"])

    def test_passes_positional_arguments_to_test_function(self):
        data = [
            {
                "description": "test-1",
                "args": [1]
            },
            {
                "description": "test-2",
                "args": [2]
            }
        ]

        expected_count = 0

        @data_driven_test(data)
        def func(argument):
            eq_(argument, expected_count)

        val = func()
        self.assert_is_an_iterable(val)

        for test in val:
            expected_count += 1
            test()

    # This is needed for methods, where "self" argument is passed to the test function
    def test_passes_positional_argument_called_with_to_tests_with_positional_arguments(self):
        stub = object()

        data = [
            {
                "description": "test-1",
                "args": [1]
            },
            {
                "description": "test-2",
                "args": [2]
            }
        ]

        expected_count = 0

        @data_driven_test(data)
        def func(param, argument):
            eq_(param, stub)
            eq_(argument, expected_count)

        val = func(stub)
        self.assert_is_an_iterable(val)

        for test in val:
            expected_count += 1
            test()

    def test_passes_keyword_arguments_to_test_function(self):
        data = [
            {
                "description": "test-1",
                "kwargs": {"arg1": 1, "arg2": 2}
            },
            {
                "description": "test-2",
                "kwargs": {"arg1": 2, "arg2": 3}
            }
        ]

        expected_count = 0

        @data_driven_test(data)
        def func(*, arg1, arg2):
            eq_(arg1, expected_count)
            eq_(arg2, arg1 + 1)

        val = func()
        self.assert_is_an_iterable(val)

        for test in val:
            expected_count += 1
            test()

    # This is needed for methods, where "self" argument is passed to the test function
    def test_passes_positional_argument_called_with_to_tests_with_keyword_arguments(self):
        stub = object()
        data = [
            {
                "description": "test-1",
                "kwargs": {"arg1": 1, "arg2": 2}
            },
            {
                "description": "test-2",
                "kwargs": {"arg1": 2, "arg2": 3}
            }
        ]

        expected_count = 0

        @data_driven_test(data)
        def func(param, *, arg1, arg2):
            eq_(param, stub)
            eq_(arg1, expected_count)
            eq_(arg2, arg1 + 1)

        stub = object()

        val = func(stub)
        self.assert_is_an_iterable(val)

        for test in val:
            expected_count += 1
            test()

    def test_passes_positional_and_keyword_arguments_to_test_function(self):
        data = [
            {
                "description": "test-1",
                "args": [0],
                "kwargs": {"arg1": 1, "arg2": 2}
            },
            {
                "description": "test-2",
                "args": [1],
                "kwargs": {"arg1": 2, "arg2": 3}
            }
        ]

        expected_count = 0

        @data_driven_test(data)
        def func(arg, *, arg1, arg2):
            eq_(arg, expected_count - 1)
            eq_(arg1, expected_count)
            eq_(arg2, arg1 + 1)

        val = func()
        self.assert_is_an_iterable(val)

        for test in val:
            expected_count += 1
            test()

    def test_passes_positional_argument_called_with_to_tests_with_positional_and_keyword_arguments(self):
        stub = object()
        data = [
            {
                "description": "test-1",
                "args": [0],
                "kwargs": {"arg1": 1, "arg2": 2}
            },
            {
                "description": "test-2",
                "args": [1],
                "kwargs": {"arg1": 2, "arg2": 3}
            }
        ]

        expected_count = 0

        @data_driven_test(data)
        def func(param, arg, *, arg1, arg2):
            eq_(param, stub)
            eq_(arg, expected_count - 1)
            eq_(arg1, expected_count)
            eq_(arg2, arg1 + 1)

        val = func(stub)
        self.assert_is_an_iterable(val)

        for test in val:
            expected_count += 1
            test()


class TestAssertMessageContains(Test):
    """py2c.tests.Test.assert_error_message_contains
    """

    def test_does_not_fail_when_given_no_required_phrases(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), []
        )

    def test_matches_complete_phrase_with_same_case(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["Hello World!"]
        )

    def test_does_not_match_complete_phrase_with_different_case(self):
        with assert_raises(AssertionError):
            self.assert_error_message_contains(
                Exception("Hello World!"), ["hello world!"]
            )

    def test_matches_overlapping_partial_phrases(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["lo ", " Wo"]
        )

    def test_matches_non_overlapping_partial_phrases(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["Hello", "World!"]
        )

    def test_matches_regardless_of_order(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["World!", "Hello"]
        )


class TestFail(Test):
    """py2c.tests.Test.fail
    """

    def test_does_causes_failure(self):
        with assert_raises(AssertionError):
            self.fail()

    def test_does_raises_exception_with_given_message(self):
        with assert_raises(AssertionError) as context:
            self.fail("EHK14H0b9DXZaT346nqx")  # random text

        eq_(context.exception.args[0], "EHK14H0b9DXZaT346nqx")

        assert context.exception.__cause__ is None

    def test_does_raises_exception_with_given_cause(self):
        err = Exception()
        try:
            raise err
        except Exception as e:
            with assert_raises(AssertionError) as context:
                self.fail(cause=e)

        assert context.exception.__cause__ is err, "Unexpected cause"

    def test_does_honours_keyword_arguments(self):
        err = Exception()
        try:
            raise err
        except Exception as e:
            with assert_raises(AssertionError) as context:
                self.fail(cause=e, message="EHK14H0b9DXZaT346nqx")

        assert context.exception.__cause__ is err, "Unexpected cause"
        eq_(context.exception.args[0], "EHK14H0b9DXZaT346nqx")

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
