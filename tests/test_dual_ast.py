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
import py2c.dual_ast as dual_ast


#-------------------------------------------------------------------------------
# A bunch of nodes used during testing
#-------------------------------------------------------------------------------
class TestNode1(dual_ast.AST):
    """Basic node
    """
    _fields = [
        ('f1', int, dual_ast.NEEDED),
    ]


class TestNode2(dual_ast.AST):
    """Node with all modifiers
    """
    _fields = [
        ('f1', int, dual_ast.NEEDED),
        ('f2', int, dual_ast.OPTIONAL),
        ('f3', int, dual_ast.ZERO_OR_MORE),
        ('f4', int, dual_ast.ONE_OR_MORE),
    ]


class TestNode3(dual_ast.AST):
    """Node with another node as child
    """
    _fields = [
        ('child', TestNode1, dual_ast.NEEDED),
    ]


class TestNode4(dual_ast.AST):
    """Equivalent to TestNode1
    """
    _fields = [
        ('f1', int, dual_ast.NEEDED),
    ]


class TestNode5(dual_ast.AST):
    """Node with invalid modifier
    """
    _fields = [
        ('f1', int, None),
    ]


class TestNode6(dual_ast.AST):
    """Node with all modifiers of identifier type
    """
    _fields = [
        ('f1', dual_ast.identifier, dual_ast.NEEDED),
        ('f2', dual_ast.identifier, dual_ast.OPTIONAL),
        ('f3', dual_ast.identifier, dual_ast.ZERO_OR_MORE),
        ('f4', dual_ast.identifier, dual_ast.ONE_OR_MORE),
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
            TestNode1()
        except dual_ast.WrongTypeError:
            self.fail("Raised exception when no arguments provided")

    def test_single(self):
        """Test for assignments on empty node
        """
        try:
            node = TestNode1(1)
        except dual_ast.WrongTypeError:
            self.fail("Raised exception when assigning valid value")
        else:
            self.assertEqual(node.f1, 1)  # pylint:disable=E1101

    def test_kwargs(self):
        try:
            node = TestNode1(f1=1)
        except dual_ast.WrongTypeError:
            self.fail("Raised exception when assigning valid value")
        else:
            self.assertEqual(node.f1, 1)  # pylint:disable=E1101

    def test_modifiers_1(self):
        """Test for modifier argument handling
        """
        try:
            node = TestNode2(1, None, (), (2,))
        except dual_ast.WrongTypeError:
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
            node = TestNode2(1, 2, (3, 4, 5), (6, 7, 8))
        except dual_ast.WrongTypeError:
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
        with self.assertRaises(dual_ast.WrongTypeError) as context:
            TestNode2(1)

        msg = context.exception.args[0]
        self.assertIn("0 or 4 positional", msg)


class NodeValidAssignmentTestCase(NodeTestCase):
    """Tests for validity checks of node valid assignments
    """
    def test_NEEDED(self):
        node = TestNode2()

        try:
            node.f1 = 1
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_OPTIONAL_1(self):
        node = TestNode2()

        try:
            node.f2 = 1
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_OPTIONAL_2(self):
        node = TestNode2()

        try:
            node.f2 = None
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_1(self):
        node = TestNode2()

        try:
            node.f3 = ()
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_2(self):
        node = TestNode2()

        try:
            node.f3 = (1,)
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_3(self):
        node = TestNode2()

        try:
            node.f3 = []
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ZERO_OR_MORE_4(self):
        node = TestNode2()

        try:
            node.f3 = [1]
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ONE_OR_MORE_1(self):
        node = TestNode2()

        try:
            node.f4 = (1,)
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")

    def test_ONE_OR_MORE_2(self):
        node = TestNode2()

        try:
            node.f4 = [1]
        except dual_ast.WrongTypeError:
            self.fail("Raised WrongTypeError for valid type")


class NodeInValidAssignmentTestCase(NodeTestCase):
    """Tests for validity checks of node valid assignments
    """
    def test_extra(self):
        node = TestNode1()
        with self.assertRaises(dual_ast.FieldError) as context:
            node.bar = 1

        msg = context.exception.args[0]
        self.assertIn("bar", msg)
        self.assertIn("no field", msg)

    def test_NEEDED_invalid_type(self):
        node = TestNode2()
        with self.assertRaises(dual_ast.WrongTypeError):
            node.f1 = ""

    def test_OPTIONAL_invalid_type(self):
        node = TestNode2()
        with self.assertRaises(dual_ast.WrongTypeError):
            node.f2 = ""

    def test_ZERO_OR_MORE_invalid_value_type(self):
        node = TestNode2()
        with self.assertRaises(dual_ast.WrongTypeError):
            node.f3 = ""

    def test_ZERO_OR_MORE_invalid_item_type_2(self):
        node = TestNode2()
        with self.assertRaises(dual_ast.WrongTypeError):
            node.f3 = [""]

    def test_ONE_OR_MORE_zero_items_1(self):
        node = TestNode2()

        with self.assertRaises(dual_ast.WrongTypeError):
            node.f4 = ()

    def test_ONE_OR_MORE_zero_items_2(self):
        node = TestNode2()

        with self.assertRaises(dual_ast.WrongTypeError):
            node.f4 = []

    def test_ONE_OR_MORE_invalid_value_type(self):
        node = TestNode2()
        with self.assertRaises(dual_ast.WrongTypeError):
            node.f4 = ""

    def test_ONE_OR_MORE_invalid_item_type_2(self):
        node = TestNode2()
        with self.assertRaises(dual_ast.WrongTypeError):
            node.f4 = [""]


class NodeFinalizationTestCase(NodeTestCase):
    """Tests for `finalize` method of nodes
    """
    def test_all_given(self):
        node = TestNode2()
        node.f1 = 1
        node.f2 = 2
        node.f3 = []
        node.f4 = [3]
        try:
            node.finalize()
        except (dual_ast.ASTError):
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, 1)
            self.assertIs(node.f2, 2)
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, (3,))

    def test_minimal_given(self):
        node = TestNode2()
        node.f1 = 1
        node.f4 = [2]
        try:
            node.finalize()
        except (dual_ast.ASTError):
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, 1)
            self.assertIs(node.f2, None)
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, (2,))

    def test_missing_attrs(self):
        with self.assertRaises(AttributeError) as context:
            TestNode2().finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("f4", msg)
        self.assertIn("missing", msg.lower())

        self.assertNotIn("f2", msg)
        self.assertNotIn("f3", msg)

    def test_child_missing_attr(self):
        node = TestNode3(TestNode1())

        with self.assertRaises(AttributeError) as context:
            node.finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("TestNode1", msg)
        self.assertIn("missing", msg.lower())

        self.assertNotIn("TestNode3", msg)

    def test_wrong_modifier(self):
        with self.assertRaises(AttributeError) as context:
            TestNode5().finalize()

        msg = context.exception.args[0]

        self.assertIn("f1", msg)
        self.assertIn("TestNode5", msg)
        self.assertIn("unknown modifier", msg.lower())

        self.assertNotIn("TestNode3", msg)


class NodeEqualityTestCase(NodeTestCase):
    """Tests for node's equality
    """
    def test_equality_1(self):
        """Test for equality (equal nodes with integer attributes)
        """
        node_1 = TestNode1(1)
        node_2 = TestNode1(1)
        node_1.finalize()
        node_2.finalize()

        self.assertEqual(node_1, node_2)

    def test_equality_2(self):
        """Test for equality with node when it has children nodes
        """
        child_node_1 = TestNode1(1)
        child_node_2 = TestNode1(1)
        node_1 = TestNode3(child_node_1)
        node_2 = TestNode3(child_node_2)
        node_1.finalize()
        node_2.finalize()

        self.assertEqual(node_1, node_2)

    def test_inequality_with_diff_value(self):
        """Test for inequality on nodes with in-equal attributes
        """
        node_1 = TestNode1(0)
        node_2 = TestNode1(1)

        self.assertNotEqual(node_1, node_2)

    def test_inequality_diff_type(self):
        """Test for inequality on the basis of type
        """
        node_1 = TestNode1(1)
        node_2 = TestNode4(1)

        self.assertNotEqual(node_1, node_2)

    def test_inequality_child(self):
        """Test for equality with node when it has children nodes
        """
        child_node_1 = TestNode1(1)
        child_node_2 = TestNode1(2)
        node_1 = TestNode3(child_node_1)
        node_2 = TestNode3(child_node_2)
        node_1.finalize()
        node_2.finalize()

        self.assertNotEqual(node_1, node_2)


class NodeReprTestCase(NodeTestCase):
    """Tests for node's string representation
    """
    def test_no_attrs(self):
        self.assertEqual(repr(TestNode1()), "TestNode1()")
        self.assertEqual(repr(TestNode2()), "TestNode2()")
        self.assertEqual(repr(TestNode3()), "TestNode3()")
        self.assertEqual(repr(TestNode4()), "TestNode4()")
        self.assertEqual(repr(TestNode5()), "TestNode5()")

    def test_some_attrs(self):
        node = TestNode2()
        node.f1 = 1
        node.f2 = None

        self.assertEqual(repr(node), "TestNode2(f1=1, f2=None)")

    def test_all_attrs(self):
        node = TestNode2()
        node.f1 = 0
        node.f2 = None
        node.f3 = (1,)
        node.f4 = (2,)

        self.assertEqual(
            repr(node), "TestNode2(f1=0, f2=None, f3=(1,), f4=(2,))"
        )


class IdentifierTestCase(unittest.TestCase):
    """Tests for 'identifier' object in the definitions
    """
    def test_init(self):
        self.assertEqual(dual_ast.identifier("valid_name"), "valid_name")
        with self.assertRaises(dual_ast.WrongAttributeValueError):
            dual_ast.identifier("Invalid name")

    def test_isinstance(self):

        self.assertIsInstance("valid_name", dual_ast.identifier)
        self.assertIsInstance(
            dual_ast.identifier("valid_name"), dual_ast.identifier
        )
        self.assertNotIsInstance("Invalid name", dual_ast.identifier)
        self.assertNotIsInstance("虎", dual_ast.identifier)

    def test_issubclass(self):
        class SubClass(dual_ast.identifier):
            pass

        self.assertTrue(issubclass(SubClass, dual_ast.identifier))
        self.assertTrue(issubclass(str, dual_ast.identifier))
        self.assertFalse(issubclass(int, dual_ast.identifier))

    def test_equality(self):
        self.assertEqual(dual_ast.identifier("name"), "name")

    def test_repr(self):
        identifier = dual_ast.identifier
        self.assertEqual(repr(identifier("a_name")), "'a_name'")
        self.assertEqual(repr(identifier("some_name")), "'some_name'")
        self.assertEqual(repr(identifier("camelCase")), "'camelCase'")

    def test_modifiers_valid_minimal(self):
        node = TestNode6()
        node.f1 = "foo"
        node.f4 = ["bar"]
        try:
            node.finalize()
        except Exception:
            self.fail("Raised Exception for valid values")

    def test_modifiers_valid_all(self):
        try:
            node = TestNode6("foo", "bar", (), ("baz",))
            node.finalize()
        except dual_ast.ASTError:
            self.fail("Raised exception when values were proper")
        else:
            self.assertEqual(node.f1, "foo")
            self.assertEqual(node.f2, "bar")
            self.assertEqual(node.f3, ())
            self.assertEqual(node.f4, ("baz",))

    def test_modifiers_invalid_values(self):
        node = TestNode6()

        with self.assertRaises(dual_ast.WrongTypeError):
            node.f1 = "invalid value"

        with self.assertRaises(dual_ast.WrongTypeError):
            node.f2 = "invalid value"

        with self.assertRaises(dual_ast.WrongTypeError):
            node.f3 = ("invalid value")

        with self.assertRaises(dual_ast.WrongTypeError):
            node.f1 = ("invalid value", "invalid value 2")


if __name__ == '__main__':
    unittest.main()
