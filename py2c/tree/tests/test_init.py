"""Unit-tests for `py2c.tree`
"""

from py2c import tree

from nose.tools import assert_raises, assert_equal, assert_not_equal
from py2c.tests import Test, data_driven_test    # noqa

import py2c.tree.tests.data_init as data


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestNode(Test):
    """py2c.tree.Node
    """

    @data_driven_test(data.Node_initialization_valid_cases, True, "initializes successfully: subclass with ")  # noqa
    def test_initialization_valid_cases(self, cls, args, kwargs, expected_dict):  # noqa
        try:
            node = cls(*args, **kwargs)
        except tree.WrongTypeError:
            self.fail("Unexpectedly raised exception")
        else:
            for name, value in expected_dict.items():
                assert_equal(getattr(node, name), value)

    @data_driven_test(data.Node_initialization_invalid_cases, True, "raises error initializing: subclass with ")  # noqa
    def test_initialization_invalid_cases(self, cls, args, kwargs, error, required_phrases):  # noqa
        with assert_raises(error) as context:
            cls(*args, **kwargs)

        self.assert_error_message_contains(context.exception, required_phrases)

    @data_driven_test(data.Node_assignment_valid_cases, True, "assigns to: ")  # noqa
    def test_assignment_valid_cases(self, cls, attr, value):  # noqa
        node = cls()

        try:
            setattr(node, attr, value)
        except Exception as e:
            self.fail("Raised error for valid assignment", e)
        else:
            assert_equal(
                getattr(node, attr), value,
                "Expected value to be set after assignment"
            )

    @data_driven_test(data.Node_assignment_invalid_cases, True, "raises error assigning to: ")  # noqa
    def test_assignment_invalid_cases(self, cls, attr, value, error_cls, required_phrases=None):  # noqa
        node = cls()

        try:
            setattr(node, attr, value)
        except error_cls as err:
            self.assert_error_message_contains(err, required_phrases or [])
        else:
            self.fail("Did not raise {} for invalid assignment".format(
                error_cls.__name__
            ))

    @data_driven_test(data.Node_finalization_valid_cases, True, "finalizes: subclass with ")  # noqa
    def test_finalization_valid_cases(self, node, final_attrs):  # noqa
        node.finalize()
        for attr, val in final_attrs.items():
            assert_equal(getattr(node, attr), val)

    @data_driven_test(data.Node_finalization_invalid_cases, True, "raises error while finalizing: subclass with ")  # noqa
    def test_finalization_invalid_cases(self, node, required_phrases):  # noqa
        try:
            node.finalize()
        except Exception as err:
            self.assert_error_message_contains(err, required_phrases)
        else:
            self.fail("Did not raise an exception for invalid finalize")

    @data_driven_test(data.Node_equality_equal_cases, True, "reports equality correctly: ")  # noqa
    def test_equality_equal_cases(self, node1, node2):  # noqa
        node1.finalize()
        node2.finalize()
        assert_equal(node1, node2)

    @data_driven_test(data.Node_equality_not_equal_cases, True, "reports in-equality correctly: ")  # noqa
    def test_equality_not_equal_cases(self, node1, node2):  # noqa
        node1.finalize()
        node2.finalize()
        assert_not_equal(node1, node2)

    @data_driven_test(data.Node_repr_cases, True, "gives correct representation: ")  # noqa
    def test_repr_cases(self, node, expected):  # noqa
        assert_equal(repr(node), expected)


# -----------------------------------------------------------------------------
# identifier tests
# -----------------------------------------------------------------------------
class TestIdentifier(Test):
    """py2c.tree.identifier
    """

    @data_driven_test(data.identifier_valid_cases, True, "initializes successfully: ")  # noqa
    def test_initialization_valid_cases(self, arg):
        obj = tree.identifier(arg)
        assert_equal(obj, arg)

    @data_driven_test(data.identifier_invalid_cases, True, "raises error when initialized: ")  # noqa
    def test_initialization_invalid_cases(self, arg):
        with assert_raises(tree.WrongAttributeValueError):
            tree.identifier(arg)

    @data_driven_test(data.identifier_valid_cases, True, "should be an instance: ")  # noqa
    def test_is_instance_cases(self, value):
        assert isinstance(value, tree.identifier)

    @data_driven_test(data.identifier_invalid_cases, True, "should not be an instance: ")  # noqa
    def test_is_instance_not_cases(self, value):
        assert not isinstance(value, tree.identifier)

    @data_driven_test(data.identifier_is_subclass_cases, True, "should be a subclass: ")  # noqa
    def test_is_subclass_cases(self, value):
        assert issubclass(value, tree.identifier)

    @data_driven_test(data.identifier_not_is_subclass_cases, True, "should not be a subclass: ")  # noqa
    def test_is_subclass_not_cases(self, value):
        assert not issubclass(value, tree.identifier)

    @data_driven_test(data.identifier_valid_cases, True, "returns argument passed as is: ")  # noqa
    def test_returns_the_value_passed(self, name):
        assert_equal(tree.identifier(name), name)
        assert type(tree.identifier(name)) == str, "Should give a str"


# -----------------------------------------------------------------------------
# fields_decorator
# -----------------------------------------------------------------------------
class TestFieldsDecorator(Test):
    """py2c.tree.fields_decorator
    """

    def test_does_behave_correctly(self):
        # TODO:: Break into multiple tests if possible.

        class Caller(object):
            called = False

            @tree.fields_decorator
            def func(cls):
                assert cls == Caller
                cls.called = True
                return 1

        assert Caller().func == 1
        assert Caller.called

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
