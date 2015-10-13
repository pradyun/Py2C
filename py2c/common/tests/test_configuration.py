"""Unit-tests for `py2c.common.configuration.Configuration`
"""

from py2c.common.configuration import (
    Configuration,
    NoSuchOptionError, InvalidOptionError
)

from nose.tools import assert_is, assert_raises, assert_equal
from py2c.tests import Test, data_driven_test


class TestConfiguration(Test):
    """py2c.common.Configuration
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

    @data_driven_test([
        {"description": "a simple name", "args": ["a_simple_name"]},
        {"description": "a dotted name", "args": ["a.dotted.name"]},
    ], prefix="registers valid option: ")
    def test_registers_valid_option(self, name):
        try:
            Configuration().register_option(name)
        except Exception:
            self.fail("Should have registered name: {}".format(name))

    @data_driven_test([
        {"description": "a name starting with dot", "args": [".invalid"]},
        {"description": "a dotted name starting with dot", "args": [".invalid.name"]},
        {"description": "a name with spaces", "args": ["invalid name"]},
        {"description": "a non-string name", "args": [1200]},
    ], prefix="raises error when registering invalid option: ")
    def test_raises_error_registering_invalid_option(self, name):
        try:
            Configuration().register_option(name)
        except Exception:
            pass
        else:
            self.fail("Should not have registered name: {}".format(name))

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
    from py2c.tests import runmodule

    runmodule(capture=False)
