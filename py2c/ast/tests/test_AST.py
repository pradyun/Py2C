"""Tests for the AST in py2c.ast
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from nose.tools import assert_raises, assert_equal, assert_not_equal

from py2c import ast
from py2c.tests import Test


#------------------------------------------------------------------------------
# A bunch of nodes used during testing
#------------------------------------------------------------------------------
class BasicNode(ast.AST):
    """Basic node
    """
    _fields = [
        ('f1', int, ast.NEEDED),
    ]


class BasicNodeCopy(ast.AST):
    """Equivalent but not equal to BasicNode
    """
    _fields = [
        ('f1', int, ast.NEEDED),
    ]


class AllIntModifersNode(ast.AST):
    """Node with all modifiers
    """
    _fields = [
        ('f1', int, ast.NEEDED),
        ('f2', int, ast.OPTIONAL),
        ('f3', int, ast.ZERO_OR_MORE),
        ('f4', int, ast.ONE_OR_MORE),
    ]


class ParentNode(ast.AST):
    """Node with another node as child
    """
    _fields = [
        ('child', BasicNode, ast.NEEDED),
    ]


class InvalidModifierNode(ast.AST):
    """Node with invalid modifier
    """
    _fields = [
        ('f1', int, None),
    ]


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestAST(Test):
    """ast.AST subclasses
    """

    def check_valid_initialization(self, cls, args, kwargs, expected_dict):
        try:
            node = cls(*args, **kwargs)
        except ast.WrongTypeError:
            self.fail("Unexpectedly raised exception")
        else:
            for name, value in expected_dict.items():
                assert_equal(getattr(node, name), value)

    def test_valid_initialization(self):
        """Tests ast.AST.__init__'s behaviour on valid initialization
        """
        yield from self.yield_tests(self.check_valid_initialization, [
            (
                "BasicNode without any arguments",
                BasicNode, [], {}, {}
            ),
            (
                "BasicNode with 1 valid positional argument",
                BasicNode, [1], {}, {"f1": 1}
            ),
            (
                "BasicNode with 1 valid keyword argument",
                BasicNode, [], {"f1": 1}, {"f1": 1}
            ),
            (
                "Node with modifers with minimal valid positional arguments",
                AllIntModifersNode, [1, None, (), (2,)], {}, {
                    "f1": 1, "f2": None, "f3": (), "f4": (2,)
                }
            ),
            (
                "Node with modifers with valid positional arguments",
                AllIntModifersNode, [1, 2, (3, 4, 5), (6, 7, 8)], {}, {
                    "f1": 1, "f2": 2, "f3": (3, 4, 5), "f4": (6, 7, 8),
                }
            )
        ], described=True, prefix="initialization of ")

    def check_invalid_initialization(self, cls, args, kwargs, error, required_phrases):  # noqa
        with assert_raises(error) as context:
            cls(*args, **kwargs)

        self.assert_message_contains(context.exception, required_phrases)

    def test_invalid_initialization(self):
        """Tests ast.AST.__init__'s behaviour on invalid initialization
        """
        yield from self.yield_tests(self.check_invalid_initialization, [
            (
                "Node with modifiers with incorrect number of arguments",
                AllIntModifersNode, [1], {},
                ast.WrongTypeError, "0 or 4 positional"
            )
        ], described=True, prefix="initialization of ")

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

    def test_assignment(self):
        """Tests ast.AST.__setattr__'s behaviour on assignments to fields.
        """
        yield from self.yield_tests(self.check_assignment, [
            (
                "NEEDED with False-ish value",
                AllIntModifersNode, "f1", 0
            ),
            (
                "NEEDED with True-ish value",
                AllIntModifersNode, "f1", 1
            ),
            (
                "OPTIONAL with False-ish value",
                AllIntModifersNode, "f2", 0
            ),
            (
                "OPTIONAL with True-ish value",
                AllIntModifersNode, "f2", 1
            ),
            (
                "OPTIONAL with None",
                AllIntModifersNode, "f2", None
            ),
            (
                "ZERO_OR_MORE with (tuple) empty",
                AllIntModifersNode, "f3", ()
            ),
            (
                "ZERO_OR_MORE with (tuple) one element",
                AllIntModifersNode, "f3", (1,)
            ),
            (
                "ZERO_OR_MORE with (tuple) four element",
                AllIntModifersNode, "f3", (1, 2, 3, 4)
            ),
            (
                "ZERO_OR_MORE with (list) empty",
                AllIntModifersNode, "f3", []
            ),
            (
                "ZERO_OR_MORE with (list) one element",
                AllIntModifersNode, "f3", [1]
            ),
            (
                "ZERO_OR_MORE with (list) four element",
                AllIntModifersNode, "f3", [1, 2, 3, 4]
            ),
            (
                "ONE_OR_MORE with (tuple) one element",
                AllIntModifersNode, "f4", (1,)
            ),
            (
                "ONE_OR_MORE with (tuple) four element",
                AllIntModifersNode, "f4", (1, 2, 3, 4)
            ),
            (
                "ONE_OR_MORE with (list) one element",
                AllIntModifersNode, "f4", [1]
            ),
            (
                "ONE_OR_MORE with (list) four element",
                AllIntModifersNode, "f4", [1, 2, 3, 4]
            ),
            (
                "non existent field",
                BasicNode, "bar", 1,
                ast.FieldError, ["bar", "no field"]
            ),
            (
                "NEEDED with incorrect type",
                AllIntModifersNode, "f1", "",
                ast.WrongTypeError
            ),
            (
                "OPTIONAL with incorrect type",
                AllIntModifersNode, "f2", "",
                ast.WrongTypeError
            ),
            (
                "ZERO_OR_MORE with incorrect type",
                AllIntModifersNode, "f3", "",
                ast.WrongTypeError
            ),
            (
                "ZERO_OR_MORE with tuple containing incorrect type",
                AllIntModifersNode, "f3", ("",),
                ast.WrongTypeError
            ),
            (
                "ZERO_OR_MORE with list containing incorrect type",
                AllIntModifersNode, "f3", [""],
                ast.WrongTypeError
            ),
            (
                "ONE_OR_MORE with incorrect type",
                AllIntModifersNode, "f4", "",
                ast.WrongTypeError
            ),
            (
                "ONE_OR_MORE with empty tuple",
                AllIntModifersNode, "f4", (),
                ast.WrongTypeError
            ),
            (
                "ONE_OR_MORE with empty list",
                AllIntModifersNode, "f4", [],
                ast.WrongTypeError
            ),
            (
                "ONE_OR_MORE with tuple containing incorrect type",
                AllIntModifersNode, "f4", ("",),
                ast.WrongTypeError
            ),
            (
                "ONE_OR_MORE with list containing incorrect type",
                AllIntModifersNode, "f4", [""],
                ast.WrongTypeError
            ),
        ], described=True, prefix="assignment to ")

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

    def test_finalize(self):
        """Tests ast.AST.finalize's behaviour on valid attributes.
        """
        yield from self.yield_tests(self.check_finalize, [
            (
                "node with all, optional included, valid arguments",
                AllIntModifersNode(1, 2, [], [3]),
                {"f1": 1, "f2": 2, "f3": (), "f4": (3,)}
            ),
            (
                "node with valid non-optional arguments",
                AllIntModifersNode(f1=1, f4=[2]),
                {"f1": 1, "f2": None, "f3": (), "f4": (2,)}
            ),
            (
                "node with missing arguments",
                AllIntModifersNode(),
                # "!f2" means check that "f2" is not in the error msg...
                None, ["f1", "f4", "missing", "!f2", "!f3"]
            ),
            (
                "node with a child with missing arguments",
                ParentNode(BasicNode()),
                None, ["missing", "f1", "BasicNode", "!ParentNode"]
            ),
            (
                "node with invalid/unknown modifier",
                InvalidModifierNode(),
                None, ["f1", "InvalidModifierNode", "unknown modifier"]
            ),
            # XXX: Add a check for child missing attribute in list, tuple...
        ], described=True, prefix="finalization of ")

    def check_equality(self, node1, node2, is_equal):
        node1.finalize()
        node2.finalize()

        if is_equal:
            assert_equal(node1, node2)
        else:
            assert_not_equal(node1, node2)

    def test_equality(self):
        """Tests ast.AST.__eq__'s behaviour
        """
        yield from self.yield_tests(self.check_equality, [
            (
                "same class nodes with equal attributes",
                BasicNode(1), BasicNode(1), True
            ),
            (
                "same class nodes with same class children with equal attributes",
                ParentNode(BasicNode(1)), ParentNode(BasicNode(1)), True
            ),
            (
                "same class nodes with non-equal attributes",
                BasicNode(0), BasicNode(1), False
            ),
            (
                "same class nodes with same class children with non-equal attributes",
                ParentNode(BasicNode(0)), ParentNode(BasicNode(1)), False
            ),
            (
                "different class nodes with same attributes",
                BasicNode(1), BasicNodeCopy(1), False
            ),
        ], described=True, prefix="equality of ")

    def check_node_repr(self, node, expected):
        assert_equal(repr(node), expected)

    def test_node_repr(self):
        """Tests ast.AST's string representation
        """
        yield from self.yield_tests(self.check_node_repr, [
            (
                "a simple, no-field node",
                BasicNode(),
                "BasicNode()"
            ),
            (
                "another simple, no-field node",
                BasicNodeCopy(),
                "BasicNodeCopy()"
            ),
            (
                "a multi-field node with no arguments",
                AllIntModifersNode(),
                "AllIntModifersNode()"
            ),
            (
                "a multi-field node (with ast.AST attributes) with no arguments",  # noqa
                ParentNode(),
                "ParentNode()"
            ),
            (
                "a node with invalid modifiers",
                InvalidModifierNode(),
                "InvalidModifierNode()"
            ),
            (
                "a multi-field node with minimal number of arguments",
                AllIntModifersNode(f1=1, f2=None),
                "AllIntModifersNode(f1=1, f2=None)"
            ),
            (
                "a multi-field node with optional arguments provided",
                AllIntModifersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6)),
                "AllIntModifersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6))"
            )
        ], described=True, prefix="check repr of ")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
