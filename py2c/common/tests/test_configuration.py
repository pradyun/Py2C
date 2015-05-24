"""Tests for the Configuration object
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

from py2c.common.configuration import (
    Configuration,
    NoSuchOptionError, InvalidOptionError
)

from nose.tools import assert_is, assert_raises, assert_equal
from py2c.tests import Test, runmodule


class TestConfiguration(Test):
    """common.Configuration
    """

    def setUp(self):
        self.config = Configuration()

    def test_does_not_set_unregistered_option(self):
        with assert_raises(NoSuchOptionError):
            self.config.set_option("unregistered_unset_option", "Won't set!")

    def test_does_not_get_unset_and_unregistered_option(self):
        with assert_raises(NoSuchOptionError):
            self.config.get_option("unregistered_unset_option")

    def test_does_get_unset_registered_option(self):
        self.config.register_option("registered_unset_option")

        val = self.config.get_option("registered_unset_option")
        assert_is(val, None)

    def test_does_set_and_get_a_registered_option(self):
        obj = object()

        self.config.register_option("registered_set_option")
        self.config.set_option("registered_set_option", obj)

        val = self.config.get_option("registered_set_option")
        assert_is(val, obj)

    def check_option_registeration(self, option_name, should_work=True):
        try:
            Configuration().register_option(option_name)
        except InvalidOptionError:
            assert not should_work, "Should have registered..."
        else:
            assert should_work, "Should not have registered..."

    def test_z_does_valid_option_registeration(self):
        yield from self.yield_tests(self.check_option_registeration, [
            ("a simple name", "a_simple_name"),
            ("a dotted name", "a.dotted.name"),
        ], described=True, prefix="does register option with ")

    def test_z_does_not_do_invalid_option_registeration(self):
        yield from self.yield_tests(self.check_option_registeration, [
            ("a name starting with dot", ".invalid", False),
            ("a dotted name starting with dot", ".invalid.name", False),
            ("a name with spaces", "invalid name", False),
            ("a non-string name", 1200, False),
        ], described=True, prefix="does not register option with ")

    def test_does_reset_options_to_default_value_correctly(self):
        self.config.register_option("option_name", "Yo!")
        # Sanity check
        assert_equal(self.config.get_option("option_name"), "Yo!")

        self.config.set_option("option_name", "Hi!")
        # Sanity check
        assert_equal(self.config.get_option("option_name"), "Hi!")

        self.config.reset()
        # Real purpose of this test
        assert_equal(self.config.get_option("option_name"), "Yo!")

if __name__ == '__main__':
    runmodule(capture=False)
