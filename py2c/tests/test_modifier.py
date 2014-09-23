#!/usr/bin/python3
"""Tests for the Matchers that are used in fixers
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

import unittest
from py2c.modifier import Modifier
from py2c.matcher import Instance


#------------------------------------------------------------------------------
# Helper classes
#------------------------------------------------------------------------------
class SimpleClass(object):
    def __init__(self):
        super().__init__()
        self.should_match = True


class SimpleModifier(Modifier):
    matcher = Instance(SimpleClass, {
        "should_match": True
    })


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class ModifierTestCase(unittest.TestCase):
    """Tests for Modifiers
    """

    def test_bad_initialization_nothing(self):
        class BadModifier(Modifier):
            pass

        with self.assertRaises(TypeError) as context:
            BadModifier()

        err = context.exception
        self.assertIn("BadModifier", err.args[0])

    def test_bad_initialization_no_modify(self):
        class BadModifier(Modifier):
            matcher = Instance(object)

        with self.assertRaises(TypeError) as context:
            BadModifier()

        err = context.exception
        self.assertIn("BadModifier", err.args[0])
        self.assertIn("modify", err.args[0])

    def test_bad_initialization_no_matcher(self):
        class BadModifier(Modifier):

            def modify(self, node):
                pass

        with self.assertRaises(AttributeError) as context:
            BadModifier()

        err = context.exception
        self.assertIn("BadModifier", err.args[0])
        self.assertIn("matcher attribute", err.args[0])

    def test_bad_initialization_matcher_is_not_Matcher(self):
        class BadModifier(Modifier):
            matcher = object()  # Not instance of py2c.matcher.Matcher

            def modify(self, node):
                pass

        with self.assertRaises(TypeError) as context:
            BadModifier()

        err = context.exception
        self.assertIn("BadModifier", err.args[0])
        self.assertIn("matcher", err.args[0])

    def test_good_initialization(self):
        class GoodModifier(Modifier):
            matcher = Instance(object)

            def modify(self, node):
                pass

        GoodModifier()

if __name__ == '__main__':
    unittest.main()
