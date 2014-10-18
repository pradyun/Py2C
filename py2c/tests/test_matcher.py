#!/usr/bin/python3
"""Tests for the Matchers that are used in modifiers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import sys
from io import StringIO

from py2c.matcher import Matcher, Instance, Attributes

from py2c.tests import Test
from nose.tools import assert_in, assert_raises


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


class Level1Class(object):
    def __init__(self):
        super().__init__()
        self.level = 1


class Level2Class(object):
    def __init__(self):
        super().__init__()
        self.level = 2
        self.object = Level1Class()


class MultiAttrClass(object):
    value_dict = {
        "int": 2,
        "float": 2.3,
        "bool": True,
        "complex": 2j,
        "str": "2.3",
        "bytes": b"2.3",
    }

    def __init__(self):
        super().__init__()
        for key, val in self.value_dict.items():
            setattr(self, key, val)


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestMatcherInheritence(Test):
    """Tests for inheritence-related behaviour of Matcher
    """

    def test_valid_matcher(self):
        try:
            matcher = SimpleMatcher()
        except Exception:
            raise
        else:
            assert matcher.match(SimpleClass())

    def test_invalid_matcher(self):
        with assert_raises(TypeError) as context:
            InvalidMatcher()

        err = context.exception
        assert_in("InvalidMatcher", err.args[0])

    def test_super_calling(self):
        with assert_raises(NotImplementedError):
            SuperCallingMatcher().match(object())


class TestAttributeMatcher(Test):
    """Tests for Attribute matcher
    """

    def check_attribute_match(self, attributes, value, should_match):
        assert_val = Attributes(attributes).match(value)
        if not should_match:
            assert_val = not assert_val
            msg = "{!r} matched Attributes({!r})"
        else:
            msg = "{!r} didn't match Attributes({!r})"
        assert assert_val, msg.format(value, attributes)

    def test_attribute_match(self):
        """Tests py2c.matcher.Attribute.match's matching
        """
        # Initial dictionary
        value_dict = MultiAttrClass.value_dict.copy()
        # Dictionary with diff value
        mismatch_value_dict = value_dict.copy()
        mismatch_value_dict["int"] += 1  # Change the value

        # Dictionary with missing value
        attr = "supposed_to_be_missing"
        assert attr not in value_dict, "{!r} was supposed to be missing.".format(attr)  # noqa
        missing_value_dict = value_dict.copy()
        missing_value_dict[attr] = None

        # Multilevel dictionary
        level2_value_dict = {
            "level": 2,
            "object": Attributes({
                "level": 1
            })
        }
        yield from self.yield_tests(self.check_attribute_match, [
            (value_dict, MultiAttrClass(), True),
            (level2_value_dict, Level2Class(), True),
            (mismatch_value_dict, MultiAttrClass(), False),
            (missing_value_dict, MultiAttrClass(), False),
        ])

    # FIXME: Clean up...
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
            self.check_attribute_match(
                bad_value_dict, MultiAttrClass(), False
            )
        except AssertionError:
            raise
        else:
            output = sys.stdout.getvalue()
            assert_in("unknown matcher", output.lower())
            assert_in("klass", output.lower())
        finally:
            sys.stdout.close()
            sys.stdout = old


class TestInstanceMatcher(Test):
    """Tests for Instance matcher
    """

    def instance_match(self, clazz, attrs=None, obj=None, should_match=True):
        match_with = obj if obj is not None else clazz()
        assert_val = Instance(clazz, attrs).match(match_with)

        if not should_match:
            assert_val = not assert_val
            msg = "{0!r} matched Instance({0.__class__.__qualname__}, {1})"
        else:
            msg = "{0!r} didn't match Instance({0.__class__.__qualname__}, {1})"  # noqa
        assert assert_val, msg.format(match_with, attrs)

    def test_instance_match(self):
        mis_match_class = MultiAttrClass()
        mis_match_class.int += 1
        yield from self.yield_tests(self.instance_match, [
            [BasicClass],
            [MultiAttrClass, MultiAttrClass.value_dict],  # noqa
            [BasicClass, None, object(), False],
            [MultiAttrClass, MultiAttrClass.value_dict, mis_match_class, False]  # noqa
        ])


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
