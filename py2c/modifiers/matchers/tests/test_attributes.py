"""Tests for the Attributes matchers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from nose.tools import assert_raises

from py2c.modifiers.matchers.attributes import Attributes
from py2c.tests import Test


#------------------------------------------------------------------------------
# Helper classes (Matching happens against these)
#------------------------------------------------------------------------------
class Level1Class(object):
    def __init__(self):
        super().__init__()
        self.level = 1


class Level2Class(object):
    def __init__(self):
        super().__init__()
        self.level = 2
        self.object = Level1Class()


# XXX: Repeated in test_instance.py
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

        with assert_raises(Exception):
            self.check_attribute_match(
                bad_value_dict, MultiAttrClass(), False
            )


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
