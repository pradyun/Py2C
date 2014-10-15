#!/usr/bin/python3
"""Tests for the AST and supporting data-types in py2c.syntax_tree
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c import syntax_tree

from py2c.tests import Test
from nose.tools import (
    nottest,
    assert_raises,
    assert_is_instance, assert_not_is_instance,
    assert_in, assert_not_in,
    assert_equal, assert_not_equal,
)


#------------------------------------------------------------------------------
# A bunch of nodes used during testing
#------------------------------------------------------------------------------
class BasicNode(syntax_tree.AST):
    """Basic node
    """
    _fields = [
        ('f1', int, syntax_tree.NEEDED),
    ]


class BasicNodeCopy(syntax_tree.AST):
    """Equivalent but not equal to BasicNode
    """
    _fields = [
        ('f1', int, syntax_tree.NEEDED),
    ]


class AllIntModifersNode(syntax_tree.AST):
    """Node with all modifiers
    """
    _fields = [
        ('f1', int, syntax_tree.NEEDED),
        ('f2', int, syntax_tree.OPTIONAL),
        ('f3', int, syntax_tree.ZERO_OR_MORE),
        ('f4', int, syntax_tree.ONE_OR_MORE),
    ]


class ParentNode(syntax_tree.AST):
    """Node with another node as child
    """
    _fields = [
        ('child', BasicNode, syntax_tree.NEEDED),
    ]


class InvalidModifierNode(syntax_tree.AST):
    """Node with invalid modifier
    """
    _fields = [
        ('f1', int, None),
    ]


class AllIdentifierModifersNode(syntax_tree.AST):
    """Node with all modifiers of identifier type
    """
    _fields = [
        ('f1', syntax_tree.identifier, syntax_tree.NEEDED),
        ('f2', syntax_tree.identifier, syntax_tree.OPTIONAL),
        ('f3', syntax_tree.identifier, syntax_tree.ZERO_OR_MORE),
        ('f4', syntax_tree.identifier, syntax_tree.ONE_OR_MORE),
    ]


class AllSingletonModifersNode(syntax_tree.AST):
    """Node with all modifiers of singleton type
    """
    _fields = [
        ('f1', syntax_tree.singleton, syntax_tree.NEEDED),
        ('f2', syntax_tree.singleton, syntax_tree.OPTIONAL),
        ('f3', syntax_tree.singleton, syntax_tree.ZERO_OR_MORE),
        ('f4', syntax_tree.singleton, syntax_tree.ONE_OR_MORE),
    ]


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestASTNode(Test):
    """Tests for behavior of syntax_tree.AST subclasses
    """

    def check_valid_initialization(self, cls, args, kwargs, expected_dict):
        try:
            node = cls(*args, **kwargs)
        except syntax_tree.WrongTypeError:
            self.fail("Unexpectedly raised exception")
        else:
            for name, value in expected_dict.items():
                assert_equal(getattr(node, name), value)

    def test_valid_initialization(self):
        """Tests syntax_tree.AST.__init__'s behaviour on valid initialization
        """
        yield from self.yield_tests(self.check_valid_initialization, [
            (BasicNode, [], {}, {}),
            (BasicNode, [1], {}, {"f1": 1}),
            (BasicNode, [], {"f1": 1}, {"f1": 1}),
            (AllIntModifersNode, [1, None, (), (2,)], {}, {
                "f1": 1, "f2": None, "f3": (), "f4": (2,)
            }),
            (AllIntModifersNode, [1, 2, (3, 4, 5), (6, 7, 8)], {}, {
                "f1": 1, "f2": 2, "f3": (3, 4, 5), "f4": (6, 7, 8),
            })
        ])

    def check_invalid_initialization(self, cls, args, kwargs, error, required_phrases):
        with assert_raises(error) as context:
            cls(*args, **kwargs)

        self.check_error_msg(context.exception, required_phrases)

    def test_invalid_initialization(self):
        """Tests syntax_tree.AST.__init__'s behaviour on invalid initialization
        """
        yield from self.yield_tests(self.check_invalid_initialization, [
            (AllIntModifersNode, [1], {}, syntax_tree.WrongTypeError, "0 or 4 positional")
        ])

    def check_valid_assignment(self, attr, value):
        node = AllIntModifersNode()

        try:
            setattr(node, attr, value)
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid assignment")
        else:
            assert_equal(getattr(node, attr), value, "Expected value to be set after assignment")

    def test_valid_assignment(self):
        """Tests syntax_tree.AST.__setattr__'s behaviour on valid assignments to fields
        """
        yield from self.yield_tests(self.check_valid_assignment, [
            ("f1", 0),
            ("f1", 1),
            ("f2", 0),
            ("f2", 1),
            ("f2", None),
            ("f3", ()),
            ("f3", (1,)),
            ("f3", (1, 2, 3, 4)),
            ("f3", []),
            ("f3", [1]),
            ("f3", [1, 2, 3, 4]),
            ("f4", (1,)),
            ("f4", (1, 2, 3, 4)),
            ("f4", [1]),
            ("f4", [1, 2, 3, 4]),
        ])

    def check_invalid_assignment(self, cls, attr, value, error, required_phrases=[]):  # noqa
        node = cls()
        with assert_raises(error) as context:
            setattr(node, attr, value)

        self.check_error_msg(context.exception, required_phrases)

    def test_invalid_assignment(self):
        """Tests syntax_tree.AST.__setattr__'s behaviour on invalid assignments to fields
        """
        yield from self.yield_tests(self.check_invalid_assignment, [
            (BasicNode, "bar", 1, syntax_tree.FieldError, ["bar", "no field"]),
            (AllIntModifersNode, "f1", "", syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f1", "", syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f2", "", syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f3", "", syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f3", (""), syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f3", [""], syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f4", "", syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f4", (), syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f4", [], syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f4", (""), syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f4", [""], syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f1", "", syntax_tree.WrongTypeError),
            (AllIntModifersNode, "f1", "", syntax_tree.WrongTypeError),

        ])

    def check_valid_finalize(self, node, final_attrs):
        try:
            node.finalize()
        except syntax_tree.ASTError:
            raise AssertionError(
                "Raised ASTError on finalize when values were OK."
            )
        else:
            for attr, val in final_attrs.items():
                assert_equal(getattr(node, attr), val)

    def test_valid_finalize(self):
        """Tests syntax_tree.AST.finalize's behaviour on valid attributes.
        """
        yield from self.yield_tests(self.check_valid_finalize, [
            (AllIntModifersNode(1, 2, [], [3]), {
                "f1": 1, "f2": 2, "f3": (), "f4": (3,)
            }),
            (AllIntModifersNode(f1=1, f4=[2]), {
                "f1": 1, "f2": None, "f3": (), "f4": (2,)
            })
        ])

    def check_invalid_finalize(self, node, required_phrases):
        with assert_raises(AttributeError) as context:
            node.finalize()

        self.check_error_msg(context.exception, required_phrases)

    def test_invalid_finalize(self):
        """Tests syntax_tree.AST.finalize's behaviour on invalid attributes \
        and modifiers.
        """
        yield from self.yield_tests(self.check_invalid_finalize, [
            # "!f2" means check that "f2" is not in the error msg...
            (AllIntModifersNode(), ["f1", "f4", "missing", "!f2", "!f3"]),
            (ParentNode(BasicNode()), ["missing", "f1", "BasicNode", "!ParentNode"]),  # noqa
            # XXX: Add a check for child missing attribute in list, tuple...
            (InvalidModifierNode(), ["f1", "InvalidModifierNode", "unknown modifier"])  # noqa
        ])

    def check_node_equality(self, node1, node2, equal):
        node1.finalize()
        node2.finalize()

        if equal:
            assert_equal(node1, node2)
        else:
            assert_not_equal(node1, node2)

    def test_node_equality(self):
        """Tests syntax_tree.AST.__eq__'s behaviour
        """
        yield from self.yield_tests(self.check_node_equality, [
            (BasicNode(1), BasicNode(1), True),
            (ParentNode(BasicNode(1)), ParentNode(BasicNode(1)), True),
            (BasicNode(0), BasicNode(1), False),
            (ParentNode(BasicNode(0)), ParentNode(BasicNode(1)), False),
            (BasicNode(1), BasicNodeCopy(1), False),
        ])

    def check_node_repr(self, node, expected):
        assert_equal(repr(node), expected)

    def test_node_repr(self):
        """Tests syntax_tree.AST's string representation
        """
        yield from self.yield_tests(self.check_node_repr, [
            (BasicNode(), "BasicNode()"),
            (AllIntModifersNode(), "AllIntModifersNode()"),
            (ParentNode(), "ParentNode()"),
            (BasicNodeCopy(), "BasicNodeCopy()"),
            (InvalidModifierNode(), "InvalidModifierNode()"),
            (
                AllIntModifersNode(f1=1, f2=None),
                "AllIntModifersNode(f1=1, f2=None)"
            ),
            (
                AllIntModifersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6)),
                "AllIntModifersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6))"
            )
        ])


# #------------------------------------------------------------------------------
# # Special Properties
# #------------------------------------------------------------------------------
class PropertyTestBase(Test):
    """Base class for tests for custom properties of the AST specification.
    """

    def check_valid_initialization(self, arg):
        assert_equal(self.class_(arg), arg)

    def check_invalid_initialization(self, arg):
        with assert_raises(syntax_tree.WrongAttributeValueError):
            self.class_(arg)

    def check_instance(self, value, is_):
        if is_:
            assert_is_instance(value, self.class_)
        else:
            assert_not_is_instance(value, self.class_)


class TestIdentifier(PropertyTestBase):
    """Tests for 'identifier' object in the definitions
    """
    class_ = syntax_tree.identifier

    def test_valid_initialization(self):
        yield from self.yield_tests(self.check_valid_initialization, [
            ["valid_name"],
            ["a_really_really_really_long_name_abcdefghijklmnopqrstuvwxyz"],
            ["a"],
        ])

    def test_invalid_initialization(self):
        yield from self.yield_tests(self.check_invalid_initialization, [
            ["Invalid name"]
        ])

    def test_isinstance(self):
        yield from self.yield_tests(self.check_instance, [
            ("valid_name", True),
            ("ValidName", True),
            ("VALID_NAME", True),
            ("Valid_1_name", True),
            (syntax_tree.identifier("valid_name"), True),
            ("valid.name", True),
            ("_valid_name_", True),
            ("_valid._attr_", True),
            ("虎", False),
            ("Invalid name", False)
        ])

    def test_issubclass(self):
        class SubClass(syntax_tree.identifier):
            pass

        assert issubclass(str, syntax_tree.identifier)
        assert issubclass(SubClass, syntax_tree.identifier)
        assert not issubclass(int, syntax_tree.identifier)

    def test_equality(self):
        assert_equal(syntax_tree.identifier("name"), "name")

    def test_repr(self):
        identifier = syntax_tree.identifier
        assert_equal(repr(identifier("a_name")), "'a_name'")
        assert_equal(repr(identifier("some_name")), "'some_name'")
        assert_equal(repr(identifier("camelCase")), "'camelCase'")

    # XXX: Clean these later
    def test_modifiers_valid_minimal(self):
        node = AllIdentifierModifersNode()
        node.f1 = "foo"
        node.f4 = ["bar"]
        try:
            node.finalize()
        except syntax_tree.ASTError:
            raise AssertionError(
                "Raised Exception for valid values"
            )

    def test_modifiers_valid_all(self):
        try:
            node = AllIdentifierModifersNode("foo", "bar", (), ("baz",))
            node.finalize()
        except syntax_tree.ASTError:
            raise AssertionError(
                "Raised exception when values were proper"
            )
        else:
            assert_equal(node.f1, "foo")
            assert_equal(node.f2, "bar")
            assert_equal(node.f3, ())
            assert_equal(node.f4, ("baz",))

    # FIXME: 4 tests in one...
    def test_modifiers_invalid_values(self):
        node = AllIdentifierModifersNode()

        with assert_raises(syntax_tree.WrongTypeError):
            node.f1 = "invalid value"

        with assert_raises(syntax_tree.WrongTypeError):
            node.f2 = "invalid value"

        with assert_raises(syntax_tree.WrongTypeError):
            node.f3 = ("invalid value")

        with assert_raises(syntax_tree.WrongTypeError):
            node.f1 = ("invalid value", "invalid value 2")


class SingletonTestCase(PropertyTestBase):
    """Tests for 'singleton' object in the definitions
    """
    class_ = syntax_tree.singleton

    def test_valid_initialization(self):
        yield from self.yield_tests(self.check_valid_initialization, [
            [True],
            [False],
            [None],
        ])

    def test_invalid_initialization(self):
        yield from self.yield_tests(self.check_invalid_initialization, [
            [""],
            [0],
            [[]],
            [()],
        ])

    def test_isinstance(self):
        yield from self.yield_tests(self.check_instance, [
            (True, True),
            (False, True),
            (None, True),
            ("string", False),
            (0, False),
            (0.0, False),
            ([], False),
            ((), False),
        ])

    def test_issubclass(self):
        class SubClass(syntax_tree.singleton):
            pass

        assert issubclass(SubClass, self._class)
        assert issubclass(bool, self._class)
        assert not issubclass(int, self._class)

    def test_repr(self):
        assert_equal(repr(syntax_tree.singleton(True)), "True")
        assert_equal(repr(syntax_tree.singleton(False)), "False")
        assert_equal(repr(syntax_tree.singleton(None)), "None")

    # XXX: Clean these later
    def test_modifiers_valid_minimal(self):
        node = AllSingletonModifersNode()
        node.f1 = None
        node.f4 = [None, True, False]
        try:
            node.finalize()
        except syntax_tree.ASTError:
            self.fail("Raised Exception for valid values")

    def test_modifiers_valid_all(self):
        try:
            node = AllSingletonModifersNode(True, None, (), (False,))
            node.finalize()
        except syntax_tree.ASTError:
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, True)
            self.assertEqual(node.f2, None)
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, (False,))

    # FIXME: 4 tests in one...
    def test_modifiers_invalid_values(self):
        node = AllSingletonModifersNode()

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f1 = 0
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f2 = 0
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f3 = (0,)
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f4 = (1, 2, 3)


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
