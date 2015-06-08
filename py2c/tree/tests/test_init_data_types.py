"""Tests supporting data-types in py2c.tree
"""

from py2c.tree import (
    identifier, WrongAttributeValueError, Node, fields_decorator
)

from py2c.tests import Test
from nose.tools import (
    assert_raises, assert_equal, assert_is_instance, assert_not_is_instance
)


# -----------------------------------------------------------------------------
# A bunch of nodes used during testing
# -----------------------------------------------------------------------------
class AllIdentifierModifersNode(Node):
    """Node with all modifiers of identifier type
    """
    _fields = [
        ('f1', identifier, 'NEEDED'),
        ('f2', identifier, 'OPTIONAL'),
        ('f3', identifier, 'ZERO_OR_MORE'),
        ('f4', identifier, 'ONE_OR_MORE'),
    ]


# -----------------------------------------------------------------------------
# Common test functionality
# -----------------------------------------------------------------------------
class DataTypeTestBase(Test):
    """Base class for tests for custom properties of the Node specification.
    """

    def check_valid_initialization(self, arg):
        obj = self.class_(arg)
        assert_equal(obj, arg)

    def check_invalid_initialization(self, arg):
        with assert_raises(WrongAttributeValueError):
            self.class_(arg)

    def check_instance(self, value, is_):
        if is_:
            assert_is_instance(value, self.class_)
        else:
            assert_not_is_instance(value, self.class_)

    def check_subclass(self, value, is_):
        if is_:
            assert issubclass(value, self.class_)
        else:
            assert not issubclass(value, self.class_)


# -----------------------------------------------------------------------------
# Data-Type specific tests
# -----------------------------------------------------------------------------
class TestIdentifier(DataTypeTestBase):
    """tree.identifier
    """
    class_ = identifier

    def test_does_initialize_with_valid_value(self):
        yield from self.yield_tests(self.check_valid_initialization, [
            ["valid name", "valid_name"],
            ["really long name", "really" * 100 + "_long_name"],
            ["short name", "a"],
        ], described=True, prefix="does initialize a ")

    def test_does_not_initialize_with_invalid_value(self):
        yield from self.yield_tests(self.check_invalid_initialization, [
            ["with spaces", "invalid name"],
            ["with hyphen", "invalid-name"],
        ], described=True, prefix="does not initialize an invalid name ")

    def test_is_an_instance(self):
        yield from self.yield_tests(self.check_instance, [
            ("a snake_case name", "valid_name", True),
            ("a CamelCase name", "ValidName", True),
            ("a LOUD_CASE name", "VALID_NAME", True),
            ("a valid name with numbers and underscore", "Valid_1_name", True),
            ("a valid identifier", identifier("valid_name"), True),
            ("an unicode character", "虎", True),  # won't ever be used :P
            (
                "a name with leading and trailing underscores",
                "_valid_name_", True
            ),
            ("an invalid name with spaces", "invalid name", False),
            ("an invalid name with dash", "invalid-name", False),
            ("an invalid name with dots", "invalid.attr", False),
        ], described=True, prefix="is an identifier instance ")

    def test_is_a_subclass(self):
        class SubClass(identifier):
            pass

        yield from self.yield_tests(self.check_subclass, [
            ("str", str, True),
            ("an inheriting sub-class", SubClass, True),
            ("int (not)", int, False),
        ], described=True, prefix="is an identifier subclass ")

    def test_is_equal_to_a_string_with_value_passed(self):
        assert_equal(identifier("name"), "name")

    def test_has_representation_that_is_consistent_with_str(self):
        assert_equal(repr(identifier("a_name")), "'a_name'")
        assert_equal(repr(identifier("some_name")), "'some_name'")
        assert_equal(repr(identifier("camelCase")), "'camelCase'")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
