"""Tests for the Matchers that are used in modifiers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from nose.tools import assert_raises

from py2c.modifiers.matchers.base_matcher import BaseMatcher
from py2c.tests import Test


#------------------------------------------------------------------------------
# Sample Matchers
#------------------------------------------------------------------------------
class SimpleMatcher(BaseMatcher):
    def match(self, node):
        return getattr(node, 'should_match', None) is True


class GenericMatcher(BaseMatcher):
    def match(self, node):
        # Do checks using generic_match
        return (
            # Built-in types
            self.generic_match(True, getattr(node, "bool", None)) and
            self.generic_match(1, getattr(node, "int", None)) and
            self.generic_match(1.1, getattr(node, "float", None)) and
            self.generic_match(1 + 2j, getattr(node, "complex", None)) and
            self.generic_match("A string", getattr(node, "string", None)) and
            # Custom matcher
            self.generic_match(SimpleMatcher(), getattr(node, "obj", None))
        )


class InvalidMatcher(BaseMatcher):
    # Doesn't implement "match"
    pass


class SuperCallingMatcher(BaseMatcher):
    def match(self, node):
        super().match(node)


#------------------------------------------------------------------------------
# Helper classes (Matching happens against these)
#------------------------------------------------------------------------------
class SimpleClass(object):
    def __init__(self):
        super().__init__()
        self.should_match = True


class GenericClass(object):
    def __init__(self):
        super().__init__()
        self.bool = True
        self.int = 1
        self.float = 1.1
        self.complex = 1 + 2j
        self.string = "A string"
        self.obj = SimpleClass()


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestMatcher(Test):
    """Tests for behaviour of BaseMatcher
    """

    def test_initialization_valid_matcher(self):
        matcher = SimpleMatcher()
        obj = SimpleClass()
        assert matcher.match(obj)

    def test_initialization_invalid_matcher(self):
        with assert_raises(TypeError) as context:
            InvalidMatcher()

        self.assert_message_contains(context.exception, ["InvalidMatcher"])

    def test_call_behaviour_super_calling_match(self):
        with assert_raises(NotImplementedError):
            SuperCallingMatcher().match(object())

    def test_generic_match_should_match(self):
        matcher = GenericMatcher()
        obj = GenericClass()
        assert matcher.match(obj)

    def test_generic_match_should_not_match(self):
        matcher = GenericMatcher()
        obj = GenericClass()
        obj.int += 1
        assert not matcher.match(obj)


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
