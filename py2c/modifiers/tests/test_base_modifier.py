#!/usr/bin/python3
"""Tests for the Matchers that are used in fixers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.matcher import Instance
from py2c.modifiers.base_modifier import BaseModifier

from py2c.tests import Test
from nose.tools import assert_raises


#------------------------------------------------------------------------------
# Helper classes
#------------------------------------------------------------------------------
class SimpleClass(object):
    def __init__(self):
        super().__init__()
        self.should_match = True


class SimpleModifier(BaseModifier):
    matcher = Instance(SimpleClass, {
        "should_match": True
    })


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestModifier(Test):
    """Tests for Modifiers
    """

    def test_good_initialization(self):
        class GoodModifier(BaseModifier):
            matcher = Instance(object)

            def modify(self, node):
                pass

        GoodModifier()

    def check_bad_initialization(self, modifier_class, err, required_phrases):
        with assert_raises(err) as context:
            modifier_class()

        self.assert_message_contains(context.exception, required_phrases)

    def test_bad_initialization(self):

        class EmptyModifier(BaseModifier):
            pass

        class NoModifyModifier(BaseModifier):
            matcher = Instance(object)

        class NoMatcherModifier(BaseModifier):

            def modify(self, node):
                pass

        class MatcherNotAMatcherModifier(BaseModifier):
            matcher = object()  # Not instance of py2c.matcher.Matcher

            def modify(self, node):
                pass

        yield from self.yield_tests(self.check_bad_initialization, [
            (EmptyModifier, TypeError, ["EmptyModifier"]),
            (NoModifyModifier, TypeError, ["NoModifyModifier", "modify"]),
            (NoMatcherModifier, AttributeError,
                ["NoMatcherModifier", "matcher", "attribute"]
            ),
            (MatcherNotAMatcherModifier, TypeError,
                [
                    "MatcherNotAMatcherModifier", "matcher", "should be",
                    "instance", "py2c.matcher.Matcher"
                ]
            ),
        ])

    def test_super_calling(self):
        class SuperCallingModifier(BaseModifier):
            matcher = Instance(object)

            def modify(self, node):
                super().modify(node)

        modifier = SuperCallingModifier()

        with assert_raises(NotImplementedError):
            modifier.modify(object())

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
