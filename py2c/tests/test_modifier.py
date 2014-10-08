#!/usr/bin/python3
"""Tests for the Matchers that are used in fixers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
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

    def test_super_calling(self):
        class SuperCallingModifier(Modifier):
            matcher = Instance(object)

            def modify(self, node):
                super().modify(node)

        modifier = SuperCallingModifier()
        with self.assertRaises(NotImplementedError):
            modifier.modify(object())

if __name__ == '__main__':
    unittest.main()
