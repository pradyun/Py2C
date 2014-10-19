#!/usr/bin/python3
"""This package contains tests for the Python-level default modifiers.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import py2c.modifiers.modifier_util

from py2c.tests import Test
from nose.tools import ok_, eq_


class PyModifierTest(Test):

    def check_modifier_result(self, modifier, node, expected):
        ok_(
            modifier.matcher.match(node),
            "Expected modifer.matcher to match node."
        )
        eq_(modifier.modify(node), expected)

    @classmethod
    def setUp(cls):
        # Clear the variable name counter
        py2c.modifiers.modifier_util.VARIABLE_HINT_COUNT = {}
