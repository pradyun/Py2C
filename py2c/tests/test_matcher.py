#!/usr/bin/python3
"""Tests for the Matchers that are used in modifiers
"""
#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

import sys
# import timeit
import unittest
from io import StringIO

from py2c.matcher import Matcher, Instance, Attributes


#------------------------------------------------------------------------------
# Sample Matchers
#------------------------------------------------------------------------------
class InvalidMatcher(Matcher):
    # Doesn't implement "match"
    pass


class SimpleMatcher(Matcher):
    def match(self, node):
        return getattr(node, 'should_match', None) is True


class SuperCallingMatcher(Matcher):
    def match(self, node):
        super().match(node)


#------------------------------------------------------------------------------
# Helper classes (Matching happens against these)
#------------------------------------------------------------------------------
class BasicClass(object):
    pass


class SimpleClass(object):
    def __init__(self):
        super().__init__()
        self.should_match = True


class Level2Class(object):
    def __init__(self):
        super().__init__()
        self.level = 2
        self.object = ClassWithMultipleAttributes()


class Level3Class(object):
    def __init__(self):
        super().__init__()
        self.level = 3
        self.object = Level2Class()


class ClassWithMultipleAttributes(object):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.int = 2
        self.float = 2.3
        self.complex = 2j
        self.bool = True
        self.str = "2.3"
        self.bytes = b"2.3"

# Match the values with ClassWithMultipleAttributes
value_dict = {
    "int": 2,
    "float": 2.3,
    "bool": True,
    "complex": 2j,
    "str": "2.3",
    "bytes": b"2.3",
}


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class MatcherTestCase(unittest.TestCase):
    """Tests for Matchers
    """


class MatcherInheritenceTestCase(MatcherTestCase):
    """Tests for inheritence-related behaviour of Matcher
    """

    def test_valid_matcher(self):
        try:
            matcher = SimpleMatcher()
        except Exception:
            raise
        else:
            self.assertTrue(matcher.match(SimpleClass()))

    def test_invalid_matcher(self):
        with self.assertRaises(TypeError) as context:
            InvalidMatcher()

        err = context.exception
        self.assertIn("InvalidMatcher", err.args[0])

    def test_super_calling(self):
        matcher = SuperCallingMatcher()
        with self.assertRaises(NotImplementedError):
            matcher.match(object())


class AttributeTestCase(MatcherTestCase):
    """Tests for Attribute matcher
    """

    def attribute_match(self, attributes, value):
        return Attributes(attributes).match(value)

    def test_attribute_basic_match(self):
        self.assertTrue(self.attribute_match(
            value_dict, ClassWithMultipleAttributes()
        ))

    def test_attribute_level2_match(self):
        level2_value_dict = {
            "level": 2,
            "object": Attributes({
                "level": 1
            })
        }

        self.assertTrue(self.attribute_match(
            level2_value_dict, Level2Class()
        ))

    def test_attribute_simple_mismatch(self):
        # Manipulate the dictionary
        mismatch_value_dict = value_dict.copy()
        mismatch_value_dict["int"] += 1  # Change a value.

        # Check for changes in matching
        self.assertFalse(self.attribute_match(
            mismatch_value_dict, ClassWithMultipleAttributes()
        ))

    def test_attribute_missing(self):
        # Make 100% sure the attribute is missing.
        attr = "supposed_to_be_missing"
        if attr in value_dict:
            self.fail("{!r} was supposed to be missing.".format(attr))
        # Manipulate the dictionary
        missing_value_dict = value_dict.copy()
        missing_value_dict[attr] = None
        # Check for changes in matching
        self.assertFalse(self.attribute_match(
            missing_value_dict, ClassWithMultipleAttributes()
        ))

    def test_attribute_invalid_matcher(self):
        class Klass(object):
            pass

        # Make sure this exists.
        bad_value_dict = {
            "int": Klass()
        }

        # Backup and Replace stdout with StringIO
        old, sys.stdout = sys.stdout, StringIO()

        try:
            self.assertFalse(self.attribute_match(
                bad_value_dict, ClassWithMultipleAttributes()
            ))
        except Exception:
            raise
        else:
            output = sys.stdout.getvalue()
            self.assertIn("unknown matcher", output.lower())
            self.assertIn("klass", output.lower())
        finally:
            sys.stdout.close()
            sys.stdout = old


class InstanceTestCase(MatcherTestCase):
    """Tests for Instance matcher
    """

    def instance_match(self, clazz, attrs=None, obj=None):
        if obj is None:
            return Instance(clazz, attrs).match(clazz())
        else:
            return Instance(clazz, attrs).match(obj)

    def test_instance_basic_match(self):
        self.assertTrue(self.instance_match(BasicClass))

    def test_instance_attribute_match(self):
        self.assertTrue(self.instance_match(
            ClassWithMultipleAttributes, value_dict
        ))

    def test_instance_mismatch(self):
        self.assertFalse(self.instance_match(BasicClass, obj=object()))

    def test_instance_attribute_mismatch(self):
        obj = ClassWithMultipleAttributes()
        obj.int += 1
        self.assertFalse(self.instance_match(
            ClassWithMultipleAttributes, value_dict, obj
        ))


if __name__ == '__main__':
    unittest.main()
