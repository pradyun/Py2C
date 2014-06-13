#!/usr/bin/python3
"""Tests for the Matchers that are used in fixers
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

import sys
import timeit
import unittest
from io import StringIO

from py2c.matcher import Matcher, Instance


#-------------------------------------------------------------------------------
# Helper classes
#-------------------------------------------------------------------------------
class BasicClass(object):
    pass


class AttributeClass(object):
    def __init__(self):
        self.int = 1
        self.float = 1.0
        self.complex = 3.0j
        self.str = "string"
        self.bytes = b"string"


class MultiLevelAttributeClass(object):
    def __init__(self):
        self.int = 1
        self.attr = AttributeClass()


#-------------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------------
class MatcherTestCase(unittest.TestCase):
    """Tests for Matcher
    """

    def test_instance_match(self):
        matcher = Instance(BasicClass)
        self.assertTrue(matcher.matches(BasicClass()))

    def test_attribute_match(self):
        matcher = Instance(AttributeClass, {
            "int": 1,
            "float": 1.0,
            "complex": 3.0j,
            "str": "string",
            "bytes": b"string",
        })
        self.assertTrue(matcher.matches(AttributeClass()))

    def test_level2_attribute_match(self):
        matcher = Instance(MultiLevelAttributeClass, {
            "int": 1,
            "attr": Instance(AttributeClass, {
                "int": 1,
                "float": 1.0,
                "complex": 3.0j,
                "str": "string",
                "bytes": b"string",
            })
        })
        self.assertTrue(matcher.matches(MultiLevelAttributeClass()))

    def test_instance_mismatch(self):
        matcher = Instance(AttributeClass)
        self.assertFalse(matcher.matches(BasicClass()))

    def test_attribute_mismatch(self):
        matcher = Instance(AttributeClass, {
            "int": 0,  # Mis-match
            "float": 1.0,
            "complex": 3.0j,
            "str": "string",
            "bytes": b"string",
        })
        self.assertFalse(matcher.matches(AttributeClass()))

    def test_level2_attribute_mismatch(self):
        matcher = Instance(MultiLevelAttributeClass, {
            "int": 1,
            "attr": Instance(AttributeClass, {
                "int": 0,  # Mis-match!
                "float": 1.0,
                "complex": 3.0j,
                "str": "string",
                "bytes": b"string",
            })
        })
        self.assertFalse(matcher.matches(MultiLevelAttributeClass()))

    # Not so sure if speed tests is a good idea...
    # def test_level2_attribute_match_speeding(self):
    #     matcher = Instance(MultiLevelAttributeClass, {
    #         "int": 1,
    #         "attr": Instance(AttributeClass, {
    #             "int": 1,
    #             "float": 1.0,
    #             "complex": 3.0j,
    #             "str": "string",
    #             "bytes": b"string",
    #         })
    #     })
    #     time = timeit.timeit(
    #         number=10000,
    #         stmt=lambda: self.assertTrue(
    #             matcher.matches(MultiLevelAttributeClass())
    #         )
    #     )
    #     # Should be 0.5, but coverage affects speed. :(
    #     self.assertLess(time, 1)

    def test_invalid_matcher(self):
        class Klass(object):
            pass

        matcher = Instance(MultiLevelAttributeClass, {
            "int": 1,
            "attr": Klass()
        })

        old = sys.stdout
        sys.stdout = StringIO()

        try:
            self.assertFalse(matcher.matches(MultiLevelAttributeClass()))
        except:
            raise
        else:
            output = sys.stdout.getvalue()
            self.assertIn("unknown matcher", output.lower())
        finally:
            sys.stdout.close()
            sys.stdout = old


if __name__ == '__main__':
    unittest.main()
