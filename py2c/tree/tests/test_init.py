"""Unit-tests for `py2c.tree`
"""

from py2c import tree

from nose.tools import (
    assert_raises,
    assert_equal, assert_not_equal,
    assert_is_instance, assert_not_is_instance,
)
from py2c.tests import Test, data_driven_test


# =============================================================================
# Helper classes
# =============================================================================
class NodeWithoutFieldsAttribute(tree.Node):
    """A base node that doesn't define the fields attribute
    """


class EmptyNode(tree.Node):
    """An empty node with no fields
    """
    _fields = []


class BasicNode(tree.Node):
    """Basic node
    """
    _fields = [
        ('f1', int, "NEEDED"),
    ]


class InheritingNodeWithoutFieldsAttributeNode(BasicNode):
    """A node that inherits from BasicNode but doesn't declare fields.

    (It should inherit the fields from parent)
    """


class BasicNodeCopy(tree.Node):
    """Equivalent but not equal to BasicNode
    """
    _fields = [
        ('f1', int, "NEEDED"),
    ]


class AllIntModifiersNode(tree.Node):
    """Node with all modifiers
    """
    _fields = [
        ('f1', int, "NEEDED"),
        ('f2', int, "OPTIONAL"),
        ('f3', int, "ZERO_OR_MORE"),
        ('f4', int, "ONE_OR_MORE"),
    ]


class NodeWithANodeField(tree.Node):
    """Node with another node as child
    """
    _fields = [
        ('child', BasicNode, "NEEDED"),
    ]


class InvalidModifierNode(tree.Node):
    """Node with invalid modifier
    """
    _fields = [
        ('f1', int, "..."),
    ]


# -----------------------------------------------------------------------------
class SubClass(tree.identifier):
    """A subclass of identifier.

    Used for checking identifier's behaviour with subclasses.
    """


# =============================================================================
# Tests
# =============================================================================
class TestNode(Test):
    """py2c.tree.Node
    """
    context = globals()

    @data_driven_test("node-initialization.yaml")
    def test_initialization(self, **kwargs):
        self.template_valid_invalid(
            self._initialization_valid, self._initialization_invalid, **kwargs
        )

    def _initialization_valid(self, node, expect):
        expect = self.load(expect)
        try:
            node = self.load(node)
        except tree.NodeError:
            self.fail("Unexpectedly raised exception")
        else:
            for name, value in expect.items():
                assert_equal(getattr(node, name), value)

    def _initialization_invalid(self, node, expect, error):
        with assert_raises(error) as context:
            self.load(node)

        self.assert_error_message_contains(context.exception, expect)

    @data_driven_test("node-assignment.yaml")
    def test_assignment(self, **kwargs):
        self.template_valid_invalid(
            self._assignment_valid, self._assignment_invalid, **kwargs
        )

    def _assignment_valid(self, node, attr, value):
        value = self.load(value)

        cls = self.load(node)
        obj = cls()

        try:
            setattr(obj, attr, value)
        except Exception as e:
            self.fail("Raised error for valid assignment", e)
        else:
            assert_equal(
                getattr(obj, attr), value,
                "Expected value to be set after assignment"
            )

    def _assignment_invalid(self, node, attr, value, error, phrases=None):
        value = self.load(value)

        cls = self.load(node)
        obj = cls()

        try:
            setattr(obj, attr, value)
        except error as err:
            self.assert_error_message_contains(err, phrases or [])
        else:
            self.fail("Did not raise {} for invalid assignment".format(
                error.__name__
            ))

    @data_driven_test("node-finalization.yaml")
    def test_finalization(self, **kwargs):
        self.template_valid_invalid(
            self._finalization_valid, self._finalization_invalid, **kwargs
        )

    def _finalization_valid(self, node, expect):
        node = self.load(node)
        expected_attrs = self.load(expect)

        node.finalize()
        for attr, val in expected_attrs.items():
            assert_equal(getattr(node, attr), val)

    def _finalization_invalid(self, node, phrases, error):
        node = self.load(node)
        with assert_raises(error) as context:
            node.finalize()
        self.assert_error_message_contains(context.exception, phrases)

    @data_driven_test("node-equality.yaml")
    def test_equality(self, node1, node2, is_equal):
        node1 = self.load(node1)
        node2 = self.load(node2)
        is_equal = self.load(is_equal)

        node1.finalize()
        node2.finalize()

        if is_equal:
            assert_equal(node1, node2)
        else:
            assert_not_equal(node1, node2)

    @data_driven_test("node-repr.yaml")
    def test_repr(self, node, expect):
        node = self.load(node)

        assert_equal(repr(node), expect)


# -----------------------------------------------------------------------------
# identifier tests
# -----------------------------------------------------------------------------
class TestIdentifier(Test):
    """py2c.tree.identifier
    """
    context = globals()

    @data_driven_test("identifier-initialization.yaml", prefix="initializes ")
    def test_initialization(self, **kwargs):
        self.template_valid_invalid(
            self._initialization_valid, self._initialization_invalid, **kwargs
        )

    def _initialization_valid(self, text):
        assert_equal(tree.identifier(text), text)

    def _initialization_invalid(self, text, error):
        with assert_raises(error):
            tree.identifier(text)

    @data_driven_test("identifier-initialization.yaml", prefix="equality of ")
    def test_equality(self, **kwargs):
        self.template_valid_invalid(
            self._isinstance_valid, self._isinstance_invalid, **kwargs
        )

    def _isinstance_valid(self, text):
        assert_is_instance(text, tree.identifier)
        assert_equal(tree.identifier(text), text)

    def _isinstance_invalid(self, text, error):
        assert_not_is_instance(text, tree.identifier)

    @data_driven_test("identifier-subclass.yaml", prefix="is-subclass of ")
    def test_subclass(self, **kwargs):
        self.template_valid_invalid(
            self._issubclass, lambda *args: None, **kwargs
        )

    def _issubclass(self, clazz, is_subclass):
        if is_subclass:
            assert issubclass(self.load(clazz), tree.identifier)
        else:
            assert not issubclass(self.load(clazz), tree.identifier)


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
