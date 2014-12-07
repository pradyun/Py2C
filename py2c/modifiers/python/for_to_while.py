"""Modify a for-loop into a while-loop based construct.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from . import PyModifier
from ..modifier_util import new_var

from py2c.matcher import Instance
from py2c.ast import python as py


class ForToWhileModifier(PyModifier):
    """Modifier that converts a for-loop into a while-loop based construct.
    """
    # Note: Consider "no_break" in variable names of this module to be
    #       "no-break" not "no break"
    matcher = Instance(py.For)

    def modify(self, node):
        # Save us from having to pass these things around...
        self.node = node

        self._target_name = new_var("for_target")
        self._iterable_name = new_var("for_iterable")
        self._no_break_var_name = new_var("for_no_break")
        self._has_else_clause = bool(node.orelse)

        retval = []
        retval.append(self._assign_iter_call())

        if self._has_else_clause:
            retval.append(self._assign_no_break(False))

        retval.append(py.While(
            test=py.NameConstant(True),
            body=self._while_loop_body()
        ))
        if self._has_else_clause:
            retval.append(self._else_clause_if())

        return retval

    def _assign_iter_call(self):
        return py.Assign(
            targets=[py.Name(id=self._iterable_name, ctx=py.Store())],
            value=py.Call(
                func=py.Name(id='iter', ctx=py.Load()),
                args=[self.node.iter],
                keywords=[],
                starargs=None,
                kwargs=None
            )
        )

    def _assign_no_break(self, value):
        return py.Assign(
            targets=[py.Name(id=self._no_break_var_name, ctx=py.Store())],
            value=py.NameConstant(value)
        )

    def _while_loop_body(self):
        body = []
        # try-except (Gets/Breaks loop)
        body.append(self._try_except_next_iter())
        # assign targets
        body.append(self._assign_loop_targets())
        # loop body
        body.extend(self._real_loop_body())
        return body

    def _try_except_next_iter(self):
        except_body = []
        if self._has_else_clause:
            except_body.append(self._assign_no_break(True))
        except_body.append(py.Break())

        try_body = []
        try_body.append(self._assign_iter_next())

        #!# try:
        #!#     <try_body>
        #!# except StopIteration:
        #!#     <except_body>
        return py.Try(
            body=try_body,
            handlers=[
                py.ExceptHandler(
                    type=py.Name(id='StopIteration', ctx=py.Load()),
                    name=None,
                    body=except_body
                )
            ],
            orelse=[],
            finalbody=[]
        )

    def _assign_iter_next(self):
        #!# target_name = iterable_name.__next__()
        return py.Assign(
            targets=[py.Name(id=self._target_name, ctx=py.Store())],
            value=py.Call(
                func=py.Attribute(
                    value=py.Name(id=self._iterable_name, ctx=py.Load()),  # noqa
                    attr='__next__',
                    ctx=py.Load()
                ),
                args=[],
                keywords=[],
                starargs=None,
                kwargs=None
            )
        )

    def _assign_loop_targets(self):
        targets = self.node.target
        if hasattr(self.node.target, "elts"):  # List, Tuple
            targets = self.node.target.elts
        else:
            targets = [self.node.target]
        return py.Assign(
            targets=targets,
            value=py.Name(id=self._target_name, ctx=py.Load())
        )

    def _real_loop_body(self):
        # If needed, create a ForLoopStart and ForLoopEnd node.
        return self.node.body

    def _else_clause_if(self):
        #!# if no_break:
        return py.If(
            test=py.Name(id=self._no_break_var_name, ctx=py.Load()),
            body=self.node.orelse,
            orelse=[]
        )
