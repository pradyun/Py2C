"""Tests for the Matchers that are used in modifiers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from nose.tools import assert_true

from py2c.modifiers.matchers.instance import Instance
from py2c.tests import Test


#------------------------------------------------------------------------------
# Helper classes (Matching happens against these)
#------------------------------------------------------------------------------
class BasicClass(object):
    pass


# XXX: Repeated in test_attributes.py
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
        assert_true(assert_val, msg.format(match_with, attrs))

    def test_instance_match(self):
        mis_match_class = MultiAttrClass()
        mis_match_class.int += 1  # We need to create the mismatch!
        yield from self.yield_tests(self.instance_match, [
            [BasicClass],
            [MultiAttrClass, MultiAttrClass.value_dict],  # noqa
            [BasicClass, None, object(), False],
            [MultiAttrClass, MultiAttrClass.value_dict, mis_match_class, False]
        ])


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
