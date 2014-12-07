"""Tests for the conversion of a for-loop into it's equaivalent while-loop
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.ast import python as py
from py2c.modifiers.python.assert_to_if_raise import AssertToIfModifier

from py2c.modifiers.python.tests import PyModifierTest


class TestAssertToIf(PyModifierTest):

    def test_assert_to_if_without_message(self):
        """Test py2c.modifiers.python.assert_to_if_raise for an assert without message.

            assert a

        """
        node = py.Assert(
            test=py.Name(id='a', ctx=py.Load()),
            msg=None
        )
        expected = py.If(
            test=py.Name(id='a', ctx=py.Load()),
            body=(
                py.Raise(
                    exc=py.Call(
                        func=py.Name(id='AssertionError', ctx=py.Load()),
                        args=[],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    ),
                    cause=None
                ),
            ),
            orelse=()
        )
        self.check_modifier_result(AssertToIfModifier(), node, expected)

    def test_assert_to_if_with_message(self):
        """Test py2c.modifiers.python.assert_to_if_raise for an assert with message.

            assert a, "text"

        """
        node = py.Assert(
            test=py.Name(id='a', ctx=py.Load()),
            msg=py.Str("text")
        )
        expected = py.If(
            test=py.Name(id='a', ctx=py.Load()),
            body=(
                py.Raise(
                    exc=py.Call(
                        func=py.Name(id='AssertionError', ctx=py.Load()),
                        args=[py.Str("text")],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    ),
                    cause=None
                ),
            ),
            orelse=()
        )
        self.check_modifier_result(AssertToIfModifier(), node, expected)

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
