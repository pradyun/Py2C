#!/usr/bin/python3
"""Tests some basic functionality provided by the py2c.tests.Test
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.tests import Test
from nose.tools import assert_equal, assert_raises


# I know that the name's horrible but it's how all tests have been named...
class TestYieldTests(Test):

    def test_empty_list(self):
        """Tests py2c.tests.Test.yield_tests with an empty list...
        """
        assert_equal(
            list(self.yield_tests(1, [])),
            []
        )

    def test_multiple_arguments(self):
        """Tests py2c.tests.Test.yield_tests with multiple arguments
        """
        assert_equal(
            list(self.yield_tests("foo", [("bar", "baz")])),
            [("foo", "bar", "baz")]
        )

    def test_argument_ordering(self):
        """Tests py2c.tests.Test.yield_tests with an ordered list of arguments.
        """
        assert_equal(
            list(self.yield_tests(1, [(2,), [3], set([4])])),
            [(1, 2), (1, 3), (1, 4)]
        )


class TestCheckErrorMsg(Test):

    def test_complete_phrase(self):
        """Tests py2c.tests.Test.assert_message_contains with same phrase.
        """
        self.assert_message_contains(
            Exception("Hello World!"), ["Hello World!"]
        )

    def test_partial_phrases_with_overlap(self):
        """Tests py2c.tests.Test.assert_message_contains with overlapping parts of the phrase.
        """
        self.assert_message_contains(
            Exception("Hello World!"), ["lo ", " Wo"]
        )

    def test_partial_phrases_without_overlap(self):
        """Tests py2c.tests.Test.assert_message_contains with non-overlapping parts of the phrase.
        """
        self.assert_message_contains(
            Exception("Hello World!"), ["Hello", "World!"]
        )

    def test_complete_phrase_diff_case(self):
        """Tests py2c.tests.Test.assert_message_contains with same phrase.
        """
        with assert_raises(AssertionError):
            self.assert_message_contains(
                Exception("Hello World!"), ["hello world!"]
            )

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
