"""Tests some basic functionality provided by the py2c.tests.Test
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

from nose.tools import assert_equal, assert_raises

from py2c.tests import Test


def check(a, b):
    return a + b


def check_order(a, b):
    return a, b


# I know that the name's horrible but it's how all tests have been named...
class TestYieldTests(Test):
    """tests.Test.yield_tests
    """

    def test_does_not_yield_values_with_empty_list(self):
        for test in self.yield_tests(check, []):
            assert False

    def test_does_yield_values_with_non_empty_list(self):
        for test in self.yield_tests(check, [("bar", "baz")]):
            assert_equal(test(), "barbaz")

    def test_does_order_arguments_correctly(self):
        li = [(0, 3), [0, 4]]
        for test, args in zip(self.yield_tests(check_order, li), li):
            assert_equal(list(test()), list(args))

    def test_is_a_generator(self):
        tests = self.yield_tests(check, [[2, 2]])

        assert_equal(next(tests)(), 4)
        with assert_raises(StopIteration):
            next(tests)

    def test_does_attach_proper_description(self):
        tests = self.yield_tests(check, [
            ["Test 0", "some_argument"],
            ("Test 1", "some_argument"),
        ], described=True)

        for i, test_method in enumerate(tests):
            assert_equal(test_method.description, "Test " + str(i))

    def test_does_attach_prefix_to_description(self):
        tests = self.yield_tests(check, [
            ["0", 0],
            ("1", 1),
        ], described=True, prefix="Test ")

        for i, test_method in enumerate(tests):
            assert_equal(test_method.description, "Test " + str(i))


class TestAssertMessageContains(Test):
    """tests.Test.assert_message_contains
    """

    def test_does_match_complete_phrase_with_same_case(self):
        self.assert_message_contains(
            Exception("Hello World!"), ["Hello World!"]
        )

    def test_does_not_match_complete_phrase_with_different_case(self):
        with assert_raises(AssertionError):
            self.assert_message_contains(
                Exception("Hello World!"), ["hello world!"]
            )

    def test_does_match_partial_phrases_overlapping(self):
        self.assert_message_contains(
            Exception("Hello World!"), ["lo ", " Wo"]
        )

    def test_does_match_partial_phrases_non_overlapping(self):
        self.assert_message_contains(
            Exception("Hello World!"), ["Hello", "World!"]
        )


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
