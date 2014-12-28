"""Tests for the ABC of Modifier
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from nose.tools import assert_raises

from py2c.modifiers.base_modifier import BaseModifier
from py2c.modifiers.matchers.base_matcher import BaseMatcher
from py2c.modifiers.tests import ModifierTest



#------------------------------------------------------------------------------
# Helper classes
#------------------------------------------------------------------------------
class SimpleMatcher(BaseMatcher):
    def match(self, node):
        return hasattr(node, "should_match")


class GoodModifier(BaseModifier):
    matcher = SimpleMatcher()

    def modify(self, node):
        pass


class EmptyModifier(BaseModifier):
    pass


class NoModifyModifier(BaseModifier):
    matcher = SimpleMatcher()


class NoMatcherModifier(BaseModifier):
    def modify(self, node):
        pass


class MatcherNotAMatcherModifier(BaseModifier):
    matcher = object()  # Not instance of BaseMatcher

    def modify(self, node):
        pass


class SuperCallingModifier(BaseModifier):
    matcher = SimpleMatcher()

    def modify(self, node):
        super().modify(node)


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestBaseModifier(ModifierTest):
    """Tests for Modifiers
    """

    def test_good_initialization(self):
        GoodModifier()

    def check_bad_initialization(self, modifier_class, err, required_phrases):
        with assert_raises(err) as context:
            modifier_class()

        self.assert_message_contains(context.exception, required_phrases)

    def test_bad_initialization(self):
        yield from self.yield_tests(self.check_bad_initialization, [
            (EmptyModifier, TypeError, ["EmptyModifier"]),
            (NoModifyModifier, TypeError, ["NoModifyModifier", "modify"]),
            (NoMatcherModifier, AttributeError, [
                "NoMatcherModifier", "matcher", "attribute"
            ]),
            (MatcherNotAMatcherModifier, TypeError, [
                "MatcherNotAMatcherModifier", "matcher", "should be",
                "instance", BaseMatcher.__qualname__
            ]),
        ])

    def test_bad_super_calling_modify(self):
        modifier = SuperCallingModifier()

        with assert_raises(NotImplementedError):
            modifier.modify(object())


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
