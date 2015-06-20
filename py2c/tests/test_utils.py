"""Unit-tests for `py2c.utils`
"""

from py2c import utils

from py2c.tests import Test
from nose.tools import assert_raises


# -----------------------------------------------------------------------------
# Helper Classes
# -----------------------------------------------------------------------------
class Namespace(object):
    pass


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestVerifyAttribute(Test):
    """py2c.utils.verify_attribute
    """

    def test_verifies_valid_case(self):
        obj = Namespace()
        obj.number = 1

        # If we see an error, it's a failed test.
        utils.verify_attribute(obj, "number", int)

    def test_does_not_allow_attribute_to_not_exist(self):
        obj = Namespace()

        with assert_raises(AttributeError) as context:
            utils.verify_attribute(obj, "number", int)

        self.assert_error_message_contains(
            context.exception,
            ["Namespace", "number", "should have"]
        )

    def test_does_not_allow_attribute_to_be_of_wrong_type(self):
        obj = Namespace()
        obj.number = "I'm not a number!"

        with assert_raises(TypeError) as context:
            utils.verify_attribute(obj, "number", int)

        self.assert_error_message_contains(
            context.exception,
            ["Namespace", "number", "should be", "instance", "int"]
        )


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestIsValidDottedIdentifier(Test):
    """py2c.utils.is_valid_dotted_identifier
    """
    # MARK:: Should this be into a data_driven_test?

    def test_verifies_valid_case(self):
        # If we see an error, it's a failed test.
        assert utils.is_valid_dotted_identifier("name")
        assert utils.is_valid_dotted_identifier("dotted.name")
        assert utils.is_valid_dotted_identifier("double.dotted.name")

    def test_does_not_allow_invalid_cases(self):
        assert not utils.is_valid_dotted_identifier("name$")
        assert not utils.is_valid_dotted_identifier("dot$ted.name")
        assert not utils.is_valid_dotted_identifier("double$.dotted.name")
        assert not utils.is_valid_dotted_identifier("double.dotted.")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
