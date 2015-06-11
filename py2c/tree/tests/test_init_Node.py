"""Unit-tests for `py2c.tree.Node`
"""

from nose.tools import assert_raises, assert_equal, assert_not_equal

from py2c import tree
from py2c.tests import Test


# -----------------------------------------------------------------------------
# A bunch of nodes used during testing
# -----------------------------------------------------------------------------
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


class InheritingNodeWithoutFieldsAttribute(BasicNode):
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
        ('f1', int, None),
    ]


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestNode(Test):
    """py2c.tree.Node
    """

    def check_valid_initialization(self, cls, args, kwargs, expected_dict):
        try:
            node = cls(*args, **kwargs)
        except tree.WrongTypeError:
            self.fail("Unexpectedly raised exception")
        else:
            for name, value in expected_dict.items():
                assert_equal(getattr(node, name), value)

    def test_does_initialize_valid_node(self):
        yield from self.yield_tests(self.check_valid_initialization, [
            (
                "zero fields without any arguments",
                EmptyNode, [], {}, {}
            ),
            (
                "one NEEDED field without any arguments",
                BasicNode, [], {}, {}
            ),
            (
                "one NEEDED field with 1 valid positional argument",
                BasicNode, [1], {}, {"f1": 1}
            ),
            (
                "one NEEDED field with 1 valid keyword argument",
                BasicNode, [], {"f1": 1}, {"f1": 1}
            ),
            (
                "all types of fields with minimal valid positional arguments",
                AllIntModifiersNode, [1, None, (), (2,)], {}, {
                    "f1": 1, "f2": None, "f3": (), "f4": (2,)
                }
            ),
            (
                "all types of fields with valid positional arguments",
                AllIntModifiersNode, [1, 2, (3, 4, 5), (6, 7, 8)], {}, {
                    "f1": 1, "f2": 2, "f3": (3, 4, 5), "f4": (6, 7, 8),
                }
            ),
            (
                "one inherited NEEDED field without any arguments",
                InheritingNodeWithoutFieldsAttribute, [], {}, {}
            ),
            (
                "one inherited NEEDED field with 1 valid positional argument",
                InheritingNodeWithoutFieldsAttribute, [1], {}, {"f1": 1}
            ),
            (
                "one inherited NEEDED field with 1 valid keyword argument",
                InheritingNodeWithoutFieldsAttribute, [], {"f1": 1}, {"f1": 1}
            ),

        ], described=True, prefix="does initialize a node with ")

    def check_invalid_initialization(self, cls, args, kwargs, error, required_phrases):  # noqa
        with assert_raises(error) as context:
            cls(*args, **kwargs)

        self.assert_message_contains(context.exception, required_phrases)

    def test_does_not_initialize_invalid_node(self):
        yield from self.yield_tests(self.check_invalid_initialization, [
            (
                "no fields attribute defined",
                NodeWithoutFieldsAttribute, [], {},
                tree.InvalidInitializationError,
                ["iterable", "_fields"]
            ),
            (
                "zero fields with some argument",
                EmptyNode, [1], {},
                tree.InvalidInitializationError,
                ["no", "arguments"]
            ),
            (
                "one field with extra arguments",
                BasicNode, [1, 2], {},
                tree.InvalidInitializationError,
                ["0 or 1", "argument", "!arguments"]
            ),
            (
                "modifiers with incorrect number of arguments",
                AllIntModifiersNode, [1], {},
                tree.InvalidInitializationError,
                ["0 or 4", "arguments"]
            ),
            (
                "missing arguments",
                AllIntModifiersNode, [1], {},
                tree.InvalidInitializationError,
                ["AllIntModifiersNode", "0 or 4", "arguments"]
            ),
            (
                "a child with missing arguments",
                lambda: NodeWithANodeField(AllIntModifiersNode(1)), [], {},
                tree.InvalidInitializationError,
                ["AllIntModifiersNode", "0 or 4", "arguments"]
            ),
            (
                "an invalid/unknown modifier",
                InvalidModifierNode, [], {},
                tree.InvalidInitializationError,
                ["InvalidModifierNode", "f1", "invalid modifier"]
            ),
        ], described=True, prefix="does not initialize a node with ")

    def check_assignment(self, cls, attr, value, error_cls=None, required_phrases=None):  # noqa
        node = cls()

        try:
            setattr(node, attr, value)
        except Exception as err:
            if error_cls is None or not isinstance(err, error_cls):
                self.fail("Raised Exception for valid assignment")
            self.assert_message_contains(err, required_phrases or [])
        else:
            if error_cls is not None:
                self.fail("Did not raise {} for invalid assignment".format(
                    error_cls.__name__
                ))
            else:
                assert_equal(
                    getattr(node, attr), value,
                    "Expected value to be set after assignment"
                )

    def test_does_assign_with_valid_values(self):
        yield from self.yield_tests(self.check_assignment, [
            (
                "NEEDED with False-ish value",
                AllIntModifiersNode, "f1", 0
            ),
            (
                "NEEDED with True-ish value",
                AllIntModifiersNode, "f1", 1
            ),
            (
                "OPTIONAL with False-ish value",
                AllIntModifiersNode, "f2", 0
            ),
            (
                "OPTIONAL with True-ish value",
                AllIntModifiersNode, "f2", 1
            ),
            (
                "OPTIONAL with None",
                AllIntModifiersNode, "f2", None
            ),
            (
                "ZERO_OR_MORE with an empty tuple",
                AllIntModifiersNode, "f3", ()
            ),
            (
                "ZERO_OR_MORE with a tuple with one element",
                AllIntModifiersNode, "f3", (1,)
            ),
            (
                "ZERO_OR_MORE with a tuple with four element",
                AllIntModifiersNode, "f3", (1, 2, 3, 4)
            ),
            (
                "ZERO_OR_MORE with an empty list",
                AllIntModifiersNode, "f3", []
            ),
            (
                "ZERO_OR_MORE with a list with one element",
                AllIntModifiersNode, "f3", [1]
            ),
            (
                "ZERO_OR_MORE with a list with four element",
                AllIntModifiersNode, "f3", [1, 2, 3, 4]
            ),
            (
                "ONE_OR_MORE with a tuple with one element",
                AllIntModifiersNode, "f4", (1,)
            ),
            (
                "ONE_OR_MORE with a tuple with four element",
                AllIntModifiersNode, "f4", (1, 2, 3, 4)
            ),
            (
                "ONE_OR_MORE with a list with one element",
                AllIntModifiersNode, "f4", [1]
            ),
            (
                "ONE_OR_MORE with a list with four element",
                AllIntModifiersNode, "f4", [1, 2, 3, 4]
            ),
        ], described=True, prefix="does assign ")

    def test_does_not_assign_with_invalid_values(self):
        yield from self.yield_tests(self.check_assignment, [
            (
                "non existent field",
                BasicNode, "bar", 1,
                tree.FieldError, ["bar", "no field"]
            ),
            (
                "NEEDED with incorrect type",
                AllIntModifiersNode, "f1", "",
                tree.WrongTypeError
            ),
            (
                "OPTIONAL with incorrect type",
                AllIntModifiersNode, "f2", "",
                tree.WrongTypeError
            ),
            (
                "ZERO_OR_MORE with incorrect type",
                AllIntModifiersNode, "f3", "",
                tree.WrongTypeError
            ),
            (
                "ZERO_OR_MORE with tuple containing incorrect type",
                AllIntModifiersNode, "f3", ("",),
                tree.WrongTypeError
            ),
            (
                "ZERO_OR_MORE with list containing incorrect type",
                AllIntModifiersNode, "f3", [""],
                tree.WrongTypeError
            ),
            (
                "ONE_OR_MORE with incorrect type",
                AllIntModifiersNode, "f4", "",
                tree.WrongTypeError
            ),
            (
                "ONE_OR_MORE with empty tuple",
                AllIntModifiersNode, "f4", (),
                tree.WrongTypeError
            ),
            (
                "ONE_OR_MORE with empty list",
                AllIntModifiersNode, "f4", [],
                tree.WrongTypeError
            ),
            (
                "ONE_OR_MORE with tuple containing incorrect type",
                AllIntModifiersNode, "f4", ("",),
                tree.WrongTypeError
            ),
            (
                "ONE_OR_MORE with list containing incorrect type",
                AllIntModifiersNode, "f4", [""],
                tree.WrongTypeError
            ),
        ], described=True, prefix="does not assign ")

    def check_finalize(self, node, final_attrs=None, required_phrases=None):  # noqa
        try:
            node.finalize()
        except Exception as err:
            if required_phrases is None:
                self.fail(
                    "Raised Exception on finalize when values were OK"
                )
            self.assert_message_contains(err, required_phrases)
        else:
            if required_phrases is not None:
                self.fail("Did not raise error for invalid finalize")
            elif final_attrs is not None:
                for attr, val in final_attrs.items():
                    assert_equal(getattr(node, attr), val)

    def test_does_finalize_node(self):
        yield from self.yield_tests(self.check_finalize, [
            (
                "valid attributes",
                AllIntModifiersNode(1, 2, [], [3]),
                {"f1": 1, "f2": 2, "f3": (), "f4": (3,)}
            ),
            (
                "valid attributes (optionals not given)",
                AllIntModifiersNode(f1=1, f4=[2]),
                {"f1": 1, "f2": None, "f3": (), "f4": (2,)}
            ),
        ], described=True, prefix="does finalize a node with ")

    def test_does_not_finalize_node(self):
        yield from self.yield_tests(self.check_finalize, [
            (
                "no parameters",
                AllIntModifiersNode(),
                None, ["missing", "f1", "f4", "!f2", "!f3"]
            ),
            (
                "a child without parameters",
                NodeWithANodeField(BasicNode()),
                None, ["missing", "f1"]
            )
        ], described=True, prefix="does not finalize a node with ")

    def check_equality(self, node1, node2, is_equal):
        node1.finalize()
        node2.finalize()

        if is_equal:
            assert_equal(node1, node2)
        else:
            assert_not_equal(node1, node2)

    def test_does_report_node_equality_correctly(self):
        yield from self.yield_tests(self.check_equality, [
            (
                "same class nodes with equal attributes",
                BasicNode(1), BasicNode(1), True
            ),
            (
                "same class nodes with same class children "
                "with equal attributes",
                NodeWithANodeField(BasicNode(1)),
                NodeWithANodeField(BasicNode(1)),
                True
            ),
        ], described=True, prefix="does report equality correctly for ")

    def test_does_report_node_inequality_correctly(self):
        yield from self.yield_tests(self.check_equality, [
            (
                "same class nodes with non-equal attributes",
                BasicNode(0), BasicNode(1), False
            ),
            (
                "same class nodes with same class children with non-equal "
                "attributes",
                NodeWithANodeField(BasicNode(0)),
                NodeWithANodeField(BasicNode(1)),
                False
            ),
            (
                "different class nodes with same attributes",
                BasicNode(1), BasicNodeCopy(1), False
            ),
        ], described=True, prefix="does report in-equality correctly for ")

    def check_node_repr(self, node, expected):
        assert_equal(repr(node), expected)

    def test_does_represent_node_correctly(self):
        yield from self.yield_tests(self.check_node_repr, [
            (
                "no-field node",
                BasicNode(),
                "BasicNode()"
            ),
            (
                "no-field node with a different name",
                BasicNodeCopy(),
                "BasicNodeCopy()"
            ),
            (
                "multi-field node with no arguments",
                AllIntModifiersNode(),
                "AllIntModifiersNode()"
            ),
            (
                "multi-field node with Node fields but no arguments",
                NodeWithANodeField(),
                "NodeWithANodeField()"
            ),
            (
                "multi-field node with minimal number of arguments",
                AllIntModifiersNode(f1=1, f2=None),
                "AllIntModifiersNode(f1=1, f2=None)"
            ),
            (
                "multi-field node with optional arguments provided",
                AllIntModifiersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6)),
                "AllIntModifiersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6))"
            )
        ], described=True, prefix="does give correct representation of a ")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
