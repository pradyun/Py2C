#!/usr/bin/python3
"""Tests for the AST used to represent Python and C in one Tree.
"""

#-------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------


import unittest
from py2c import syntax_tree


#-------------------------------------------------------------------------------
# A bunch of nodes used during testing
#-------------------------------------------------------------------------------
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


#-------------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------------
class NodeTestCase(unittest.TestCase):
    """Tests for nodes
    """


class NodeInitializationTestCase(NodeTestCase):
    """Tests for the initialization of the values of nodes
    """
    def test_empty(self):
        """Test for empty initialization
        """
        try:
            BasicNode()
        except syntax_tree.WrongTypeError:
            self.fail("Raised exception when no arguments provided")

    def test_single(self):
        """Test for assignments on empty node
        """
        try:
            node = BasicNode(1)
        except syntax_tree.WrongTypeError:
            self.fail("Raised exception when assigning valid value")
        else:
            self.assertEqual(node.f1, 1)  # pylint:disable=E1101

    def test_kwargs(self):
        try:
            node = BasicNode(f1=1)
        except syntax_tree.WrongTypeError:
            self.fail("Raised exception when assigning valid value")
        else:
            self.assertEqual(node.f1, 1)  # pylint:disable=E1101

    def test_modifiers_1(self):
        """Test for modifier argument handling
        """
        try:
            node = AllIntModifersNode(1, None, (), (2,))
        except syntax_tree.WrongTypeError:
            self.fail("Raised exception for valid values")
        else:
            # pylint:disable=E1101
            self.assertEqual(node.f1, 1)
            self.assertEqual(node.f2, None)
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, (2,))

    def test_modifiers_2(self):
        """Test for modifier argument handling
        """
        try:
            node = AllIntModifersNode(1, 2, (3, 4, 5), (6, 7, 8))
        except syntax_tree.WrongTypeError:
            self.fail("Raised exception for valid values")
        else:
            # pylint:disable=E1101
            self.assertEqual(node.f1, 1)
            self.assertEqual(node.f2, 2)
            self.assertEqual(node.f3, (3, 4, 5))
            self.assertEqual(node.f4, (6, 7, 8))

    def test_invalid(self):
        """Test for raising error for wrong number of arguments
        """
        with self.assertRaises(syntax_tree.WrongTypeError) as context:
            AllIntModifersNode(1)

        msg = context.exception.args[0]
        self.assertIn("0 or 4 positional", msg)


class NodeValidAssignmentTestCase(NodeTestCase):
    """Tests for validity checks of node valid assignments
    """
    def test_NEEDED(self):
        node = AllIntModifersNode()

        try:
            node.f1 = 1
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_OPTIONAL_1(self):
        node = AllIntModifersNode()

        try:
            node.f2 = 1
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_OPTIONAL_2(self):
        node = AllIntModifersNode()

        try:
            node.f2 = None
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_1(self):
        node = AllIntModifersNode()

        try:
            node.f3 = ()
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_2(self):
        node = AllIntModifersNode()

        try:
            node.f3 = (1,)
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_3(self):
        node = AllIntModifersNode()

        try:
            node.f3 = []
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_4(self):
        node = AllIntModifersNode()

        try:
            node.f3 = [1]
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ONE_OR_MORE_1(self):
        node = AllIntModifersNode()

        try:
            node.f4 = (1,)
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ONE_OR_MORE_2(self):
        node = AllIntModifersNode()

        try:
            node.f4 = [1]
        except syntax_tree.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")


class NodeInValidAssignmentTestCase(NodeTestCase):
    """Tests for validity checks of node valid assignments
    """
    def test_extra(self):
        node = BasicNode()
        with self.assertRaises(syntax_tree.FieldError) as context:
            node.bar = 1

        msg = context.exception.args[0]
        self.assertIn("bar", msg)
        self.assertIn("no field", msg)

    def test_NEEDED_invalid_type(self):
        node = AllIntModifersNode()
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f1 = ""

    def test_OPTIONAL_invalid_type(self):
        node = AllIntModifersNode()
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f2 = ""

    def test_ZERO_OR_MORE_invalid_value_type(self):
        node = AllIntModifersNode()
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f3 = ""

    def test_ZERO_OR_MORE_invalid_item_type_2(self):
        node = AllIntModifersNode()
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f3 = [""]

    def test_ONE_OR_MORE_zero_items_1(self):
        node = AllIntModifersNode()

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f4 = ()

    def test_ONE_OR_MORE_zero_items_2(self):
        node = AllIntModifersNode()

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f4 = []

    def test_ONE_OR_MORE_invalid_value_type(self):
        node = AllIntModifersNode()
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f4 = ""

    def test_ONE_OR_MORE_invalid_item_type_2(self):
        node = AllIntModifersNode()
        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f4 = [""]


class NodeFinalizationTestCase(NodeTestCase):
    """Tests for `finalize` method of nodes
    """
    def test_all_given(self):
        node = AllIntModifersNode()
        node.f1 = 1
        node.f2 = 2
        node.f3 = []
        node.f4 = [3]
        try:
            node.finalize()
        except (syntax_tree.ASTError):
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, 1)
            self.assertIs(node.f2, 2)
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, (3,))

    def test_minimal_given(self):
        node = AllIntModifersNode()
        node.f1 = 1
        node.f4 = [2]
        try:
            node.finalize()
        except (syntax_tree.ASTError):
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, 1)
            self.assertIs(node.f2, None)
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, (2,))

    def test_missing_attrs(self):
        with self.assertRaises(AttributeError) as context:
            AllIntModifersNode().finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("f4", msg)
        self.assertIn("missing", msg.lower())

        self.assertNotIn("f2", msg)
        self.assertNotIn("f3", msg)

    def test_child_missing_attr(self):
        node = ParentNode(BasicNode())

        with self.assertRaises(AttributeError) as context:
            node.finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("BasicNode", msg)
        self.assertIn("missing", msg.lower())

        self.assertNotIn("ParentNode", msg)

    def test_child_in_list_missing_attr(self):
        node = ParentNode(BasicNode())

        with self.assertRaises(AttributeError) as context:
            node.finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("BasicNode", msg)
        self.assertIn("missing", msg.lower())

        self.assertNotIn("ParentNode", msg)

    def test_wrong_modifier(self):
        with self.assertRaises(AttributeError) as context:
            InvalidModifierNode().finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("InvalidModifierNode", msg)
        self.assertIn("unknown modifier", msg.lower())

        self.assertNotIn("ParentNode", msg)


class NodeEqualityTestCase(NodeTestCase):
    """Tests for node's equality
    """
    def test_equality_1(self):
        """Test for equality (equal nodes with integer attributes)
        """
        node_1 = BasicNode(1)
        node_2 = BasicNode(1)
        node_1.finalize()
        node_2.finalize()

        self.assertEqual(node_1, node_2)

    def test_equality_2(self):
        """Test for equality with node when it has children nodes
        """
        child_node_1 = BasicNode(1)
        child_node_2 = BasicNode(1)
        node_1 = ParentNode(child_node_1)
        node_2 = ParentNode(child_node_2)
        node_1.finalize()
        node_2.finalize()

        self.assertEqual(node_1, node_2)

    def test_inequality_with_diff_value(self):
        """Test for inequality on nodes with in-equal attributes
        """
        node_1 = BasicNode(0)
        node_2 = BasicNode(1)

        self.assertNotEqual(node_1, node_2)

    def test_inequality_diff_type(self):
        """Test for inequality on the basis of type
        """
        node_1 = BasicNode(1)
        node_2 = BasicNodeCopy(1)

        self.assertNotEqual(node_1, node_2)

    def test_inequality_child(self):
        """Test for equality with node when it has children nodes
        """
        child_node_1 = BasicNode(1)
        child_node_2 = BasicNode(2)
        node_1 = ParentNode(child_node_1)
        node_2 = ParentNode(child_node_2)
        node_1.finalize()
        node_2.finalize()

        self.assertNotEqual(node_1, node_2)


class NodeReprTestCase(NodeTestCase):
    """Tests for node's string representation
    """
    def test_no_attrs(self):
        self.assertEqual(repr(BasicNode()), "BasicNode()")
        self.assertEqual(repr(AllIntModifersNode()), "AllIntModifersNode()")
        self.assertEqual(repr(ParentNode()), "ParentNode()")
        self.assertEqual(repr(BasicNodeCopy()), "BasicNodeCopy()")
        self.assertEqual(repr(InvalidModifierNode()), "InvalidModifierNode()")

    def test_some_attrs(self):
        node = AllIntModifersNode()
        node.f1 = 1
        node.f2 = None

        self.assertEqual(repr(node), "AllIntModifersNode(f1=1, f2=None)")

    def test_all_attrs(self):
        node = AllIntModifersNode()
        node.f1 = 0
        node.f2 = None
        node.f3 = (1,)
        node.f4 = (2,)

        self.assertEqual(
            repr(node), "AllIntModifersNode(f1=0, f2=None, f3=(1,), f4=(2,))"
        )


class IdentifierTestCase(unittest.TestCase):
    """Tests for 'identifier' object in the definitions
    """
    def test_init(self):
        self.assertEqual(syntax_tree.identifier("valid_name"), "valid_name")
        with self.assertRaises(syntax_tree.WrongAttributeValueError):
            syntax_tree.identifier("Invalid name")

    def test_isinstance(self):

        self.assertIsInstance("valid_name", syntax_tree.identifier)
        self.assertIsInstance("ValidName", syntax_tree.identifier)
        self.assertIsInstance("VALID_NAME", syntax_tree.identifier)
        self.assertIsInstance("Valid_1_name", syntax_tree.identifier)
        self.assertIsInstance(
            syntax_tree.identifier("valid_name"), syntax_tree.identifier
        )
        self.assertIsInstance("valid.name", syntax_tree.identifier)
        self.assertIsInstance("_valid_name_", syntax_tree.identifier)
        self.assertIsInstance("_valid._name", syntax_tree.identifier)

        self.assertNotIsInstance("Invalid name", syntax_tree.identifier)
        self.assertNotIsInstance("虎", syntax_tree.identifier)

    def test_issubclass(self):
        class SubClass(syntax_tree.identifier):
            pass

        self.assertTrue(issubclass(SubClass, syntax_tree.identifier))
        self.assertTrue(issubclass(str, syntax_tree.identifier))
        self.assertFalse(issubclass(int, syntax_tree.identifier))

    def test_equality(self):
        self.assertEqual(syntax_tree.identifier("name"), "name")

    def test_repr(self):
        identifier = syntax_tree.identifier
        self.assertEqual(repr(identifier("a_name")), "'a_name'")
        self.assertEqual(repr(identifier("some_name")), "'some_name'")
        self.assertEqual(repr(identifier("camelCase")), "'camelCase'")

    def test_modifiers_valid_minimal(self):
        node = AllIdentifierModifersNode()
        node.f1 = "foo"
        node.f4 = ["bar"]
        try:
            node.finalize()
        except syntax_tree.ASTError:
            self.fail("Raised Exception for valid values")

    def test_modifiers_valid_all(self):
        try:
            node = AllIdentifierModifersNode("foo", "bar", (), ("baz",))
            node.finalize()
        except syntax_tree.ASTError:
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, "foo")
            self.assertEqual(node.f2, "bar")
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, ("baz",))

    def test_modifiers_invalid_values(self):
        node = AllIdentifierModifersNode()

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f1 = "invalid value"

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f2 = "invalid value"

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f3 = ("invalid value")

        with self.assertRaises(syntax_tree.WrongTypeError):
            node.f1 = ("invalid value", "invalid value 2")


if __name__ == '__main__':
    unittest.main()
