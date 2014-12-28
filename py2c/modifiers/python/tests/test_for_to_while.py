"""Tests for the conversion of a for-loop into it's equaivalent while-loop
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.ast import python as py
from py2c.modifiers.python.for_to_while import ForToWhileModifier

from py2c.modifiers.python.tests import PyModifierTest


class TestForToWhile(PyModifierTest):
    def test_for_to_while_without_else_clause(self):
        """Test py2c.modifiers.python.for_to_while for a for loop without else.

            for a in some_list:
                print(a)

        """
        node = py.For(
            target=py.Name(id='a', ctx=py.Store()),
            iter=py.Name(id='some_list', ctx=py.Load()),
            body=[
                py.Expr(
                    value=py.Call(
                        func=py.Name(id='print', ctx=py.Load()),
                        args=[
                            py.Name(id='a', ctx=py.Load())
                        ],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    )
                )
            ],
            orelse=[]
        )
        expected = [
            py.Assign(
                targets=[
                    py.Name(id='__py2c_for_iterable_1__', ctx=py.Store())
                ],
                value=py.Call(
                    func=py.Name(id='iter', ctx=py.Load()),
                    args=[
                        py.Name(id='some_list', ctx=py.Load())
                    ],
                    keywords=[],
                    starargs=None,
                    kwargs=None
                )
            ),
            py.While(
                test=py.NameConstant(value=True),
                body=[
                    py.Try(
                        body=[
                            py.Assign(
                                targets=[
                                    py.Name(id='__py2c_for_target_1__', ctx=py.Store())  # noqa
                                ],
                                value=py.Call(
                                    func=py.Attribute(
                                        value=py.Name(id='__py2c_for_iterable_1__', ctx=py.Load()),  # noqa
                                        attr='__next__',
                                        ctx=py.Load()
                                    ),
                                    args=[],
                                    keywords=[],
                                    starargs=None,
                                    kwargs=None
                                )
                            )
                        ],
                        handlers=[
                            py.ExceptHandler(
                                type=py.Name(id='StopIteration', ctx=py.Load()),
                                name=None,
                                body=[
                                    py.Break()
                                ]
                            )
                        ],
                        orelse=[],
                        finalbody=[]
                    ),
                    py.Assign(
                        targets=[
                            py.Name(id='a', ctx=py.Store())
                        ],
                        value=py.Name(id='__py2c_for_target_1__', ctx=py.Load())
                    ),
                    py.Expr(
                        value=py.Call(
                            func=py.Name(id='print', ctx=py.Load()),
                            args=[
                                py.Name(id='a', ctx=py.Load())
                            ],
                            keywords=[],
                            starargs=None,
                            kwargs=None
                        )
                    )
                ],
            )
        ]

        self.check_modifier_result(ForToWhileModifier(), node, expected)

    def test_for_to_while_with_else_clause(self):
        """Test py2c.modifiers.python.for_to_while for a for loop with else.

            for a,b in some_list:
                print("In Body")
            else:
                print("In Else")
        """
        node = py.For(
            target=py.Tuple(
                elts=[
                    py.Name(id='a', ctx=py.Store()),
                    py.Name(id='b', ctx=py.Store())
                ],
                ctx=py.Store()
            ),
            iter=py.Name(id='some_list', ctx=py.Load()),
            body=[
                py.Expr(
                    value=py.Call(
                        func=py.Name(id='print', ctx=py.Load()),
                        args=[
                            py.Str(s="In Body")
                        ],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    )
                )
            ],
            orelse=[
                py.Expr(
                    value=py.Call(
                        func=py.Name(id='print', ctx=py.Load()),
                        args=[
                            py.Str(s="In Else")
                        ],
                        keywords=[],
                        starargs=None,
                        kwargs=None
                    )
                )
            ]
        )
        expected = [
            py.Assign(
                targets=[
                    py.Name(id='__py2c_for_iterable_1__', ctx=py.Store())
                ],
                value=py.Call(
                    func=py.Name(id='iter', ctx=py.Load()),
                    args=[
                        py.Name(id='some_list', ctx=py.Load())
                    ],
                    keywords=[],
                    starargs=None,
                    kwargs=None
                )
            ),
            py.Assign(
                targets=[
                    py.Name(id='__py2c_for_no_break_1__', ctx=py.Store())
                ],
                value=py.NameConstant(value=False)
            ),
            py.While(
                test=py.NameConstant(value=True),
                body=[
                    py.Try(
                        body=[
                            py.Assign(
                                targets=[
                                    py.Name(id='__py2c_for_target_1__', ctx=py.Store())  # noqa
                                ],
                                value=py.Call(
                                    func=py.Attribute(
                                        value=py.Name(id='__py2c_for_iterable_1__', ctx=py.Load()),  # noqa
                                        attr='__next__',
                                        ctx=py.Load()
                                    ),
                                    args=[],
                                    keywords=[],
                                    starargs=None,
                                    kwargs=None
                                )
                            )
                        ],
                        handlers=[
                            py.ExceptHandler(
                                type=py.Name(id='StopIteration', ctx=py.Load()),
                                name=None,
                                body=[
                                    py.Assign(
                                        targets=[
                                            py.Name(id='__py2c_for_no_break_1__', ctx=py.Store())  # noqa
                                        ],
                                        value=py.NameConstant(value=True)
                                    ),
                                    py.Break()
                                ]
                            )
                        ],
                        orelse=[],
                        finalbody=[]
                    ),
                    py.Assign(
                        targets=[
                            py.Name(id='a', ctx=py.Store()),
                            py.Name(id='b', ctx=py.Store())
                        ],
                        value=py.Name(id='__py2c_for_target_1__', ctx=py.Load())
                    ),
                    py.Expr(
                        value=py.Call(
                            func=py.Name(id='print', ctx=py.Load()),
                            args=[
                                py.Str(
                                    s='In Body'
                                )
                            ],
                            keywords=[],
                            starargs=None,
                            kwargs=None
                        )
                    )
                ],
            ),
            py.If(
                test=py.Name(id="__py2c_for_no_break_1__", ctx=py.Load()),
                body=[
                    py.Expr(
                        value=py.Call(
                            func=py.Name(id='print', ctx=py.Load()),
                            args=[
                                py.Str(s="In Else")
                            ],
                            keywords=[],
                            starargs=None,
                            kwargs=None
                        )
                    )
                ],
                orelse=[]
            )
        ]

        self.check_modifier_result(ForToWhileModifier(), node, expected)


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
