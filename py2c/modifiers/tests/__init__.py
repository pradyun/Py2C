"""This package contains tests for the modifier infrastructure.
"""

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
        # Clear the variable name counter
        modifier_util.VARIABLE_HINT_COUNT = {}
