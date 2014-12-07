"""Tests some basic functionality provided by the py2c.tests.Test
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.tests import Test
from nose.tools import assert_equal, assert_not_equal, assert_raises


# I know that the name's horrible but it's how all tests have been named...
class TestYieldTests(Test):

    def test_empty_list(self):
        assert_equal(
            list(self.yield_tests(object(), [])),
            []
        )

    def test_multiple_arguments(self):
        assert_equal(
            list(self.yield_tests("foo", [("bar", "baz")])),
            [("foo", "bar", "baz")]
        )

    def test_argument_ordering(self):
        assert_equal(
            list(self.yield_tests(1, [(2,), [3], set([4])])),
            [(1, 2), (1, 3), (1, 4)]
        )

    def test_generator_behaviour(self):
        tests = self.yield_tests(1, [[2], [3], [4]])

        assert_not_equal(tests, [(1, 2), (1, 3), (1, 4)])
        assert_equal(next(tests), (1, 2))
        assert_equal(next(tests), (1, 3))
        assert_equal(next(tests), (1, 4))
        with assert_raises(StopIteration):
            next(tests)


class TestCheckErrorMsg(Test):

    def test_complete_phrase_with_same_case(self):
        self.assert_message_contains(
            Exception("Hello World!"), ["Hello World!"]
        )

    def test_complete_phrase_with_different_case(self):
        with assert_raises(AssertionError):
            self.assert_message_contains(
                Exception("Hello World!"), ["hello world!"]
            )

    def test_partial_phrases_overlapping(self):
        self.assert_message_contains(
            Exception("Hello World!"), ["lo ", " Wo"]
        )

    def test_partial_phrases_non_overlapping(self):
        self.assert_message_contains(
            Exception("Hello World!"), ["Hello", "World!"]
        )

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
