"""This package contains tests for the modifiers and related infrastructure.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.modifiers import modifier_util

from py2c.tests import Test
from nose.tools import ok_, eq_


class ModifierTest(Test):

    def check_modifier_result(self, modifier, node, expected):
        ok_(
            modifier.matcher.match(node),
            "Expected modifer.matcher to match node."
        )
        eq_(modifier.modify(node), expected)

    @classmethod
    def setUp(cls):
        # Reset the variables in modifier util.
        modifier_util.reset()
