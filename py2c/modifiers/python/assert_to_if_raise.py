"""Modify an assert statement into an if statement.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from . import PyModifier

from py2c.matcher import Instance
from py2c.syntax_tree.python import Assert, If, Raise, Call, Name, Load


class AssertToIfModifier(PyModifier):
    """Modifier that converts an assert stmt into an if stmt.
    """

    matcher = Instance(Assert)

    def modify(self, node):
        return If(
            test=node.test,
            body=(
                Raise(
                    exc=Call(
                        func=Name(id='AssertionError', ctx=Load()),
                        args=[node.msg] if node.msg else [],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    ),
                    cause=None
                ),
            ),
            orelse=()
        )
