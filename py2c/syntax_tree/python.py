#!/usr/bin/python3
"""Holds all AST definitions in this package by importing them.
"""

#---------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#---------------------------------------------------------------------------
from . import (
    AST,
    identifier,
    NEEDED, OPTIONAL, ONE_OR_MORE, ZERO_OR_MORE
)


class PyAST(AST):
    _fields = AST._fields


class mod(PyAST):
    _fields = PyAST._fields


class stmt(PyAST):
    _fields = PyAST._fields


class expr(PyAST):
    _fields = PyAST._fields


class expr_context(PyAST):
    _fields = PyAST._fields


class slice(PyAST):
    _fields = PyAST._fields


class boolop(PyAST):
    _fields = PyAST._fields


class operator(PyAST):
    _fields = PyAST._fields


class unaryop(PyAST):
    _fields = PyAST._fields


class cmpop(PyAST):
    _fields = PyAST._fields


class arg(PyAST):
    _fields = PyAST._fields + [
        ('arg', identifier, NEEDED),
        ('annotation', expr, OPTIONAL),
    ]


class comprehension(PyAST):
    _fields = PyAST._fields + [
        ('target', expr, NEEDED),
        ('iter', expr, NEEDED),
        ('ifs', expr, ZERO_OR_MORE),
    ]


class arguments(PyAST):
    _fields = PyAST._fields + [
        ('args', arg, ZERO_OR_MORE),
        ('vararg', identifier, OPTIONAL),
        ('varargannotation', expr, OPTIONAL),
        ('kwonlyargs', arg, ZERO_OR_MORE),
        ('kwarg', identifier, OPTIONAL),
        ('kwargannotation', expr, OPTIONAL),
        ('defaults', expr, ZERO_OR_MORE),
        ('kw_defaults', expr, ZERO_OR_MORE),
    ]


class keyword(PyAST):
    _fields = PyAST._fields + [
        ('arg', identifier, NEEDED),
        ('value', expr, NEEDED),
    ]


class alias(PyAST):
    _fields = PyAST._fields + [
        ('name', identifier, NEEDED),
        ('asname', identifier, OPTIONAL),
    ]


class withitem(PyAST):
    _fields = PyAST._fields + [
        ('context_expr', expr, NEEDED),
        ('optional_vars', expr, OPTIONAL),
    ]


class ExceptHandler(PyAST):
    _fields = PyAST._fields + [
        ('type', expr, OPTIONAL),
        ('name', identifier, OPTIONAL),
        ('body', stmt, ZERO_OR_MORE),
    ]


class Module(mod):
    _fields = mod._fields + [
        ('body', stmt, ZERO_OR_MORE),
    ]


class FunctionDef(stmt):
    _fields = stmt._fields + [
        ('name', identifier, NEEDED),
        ('args', arguments, NEEDED),
        ('body', stmt, ZERO_OR_MORE),
        ('decorator_list', expr, ZERO_OR_MORE),
        ('returns', expr, OPTIONAL),
    ]


class ClassDef(stmt):
    _fields = stmt._fields + [
        ('name', identifier, NEEDED),
        ('bases', expr, ZERO_OR_MORE),
        ('keywords', keyword, ZERO_OR_MORE),
        ('starargs', expr, OPTIONAL),
        ('kwargs', expr, OPTIONAL),
        ('body', stmt, ZERO_OR_MORE),
        ('decorator_list', expr, ZERO_OR_MORE),
    ]


class Return(stmt):
    _fields = stmt._fields + [
        ('value', expr, OPTIONAL),
    ]


class Delete(stmt):
    _fields = stmt._fields + [
        ('targets', expr, ZERO_OR_MORE),
    ]


class Assign(stmt):
    _fields = stmt._fields + [
        ('targets', expr, ZERO_OR_MORE),
        ('value', expr, NEEDED),
    ]


class AugAssign(stmt):
    _fields = stmt._fields + [
        ('target', expr, NEEDED),
        ('op', operator, NEEDED),
        ('value', expr, NEEDED),
    ]


class For(stmt):
    _fields = stmt._fields + [
        ('target', expr, NEEDED),
        ('iter', expr, NEEDED),
        ('body', stmt, ZERO_OR_MORE),
        ('orelse', stmt, ZERO_OR_MORE),
    ]


class While(stmt):
    _fields = stmt._fields + [
        ('test', expr, NEEDED),
        ('body', stmt, ZERO_OR_MORE),
        ('orelse', stmt, ZERO_OR_MORE),
    ]


class If(stmt):
    _fields = stmt._fields + [
        ('test', expr, NEEDED),
        ('body', stmt, ZERO_OR_MORE),
        ('orelse', stmt, ZERO_OR_MORE),
    ]


class With(stmt):
    _fields = stmt._fields + [
        ('items', withitem, ZERO_OR_MORE),
        ('body', stmt, ZERO_OR_MORE),
    ]


class Raise(stmt):
    _fields = stmt._fields + [
        ('exc', expr, OPTIONAL),
        ('cause', expr, OPTIONAL),
    ]


class Try(stmt):
    _fields = stmt._fields + [
        ('body', stmt, ZERO_OR_MORE),
        ('handlers', ExceptHandler, ZERO_OR_MORE),
        ('orelse', stmt, ZERO_OR_MORE),
        ('finalbody', stmt, ZERO_OR_MORE),
    ]


class Assert(stmt):
    _fields = stmt._fields + [
        ('test', expr, NEEDED),
        ('msg', expr, OPTIONAL),
    ]


class Import(stmt):
    _fields = stmt._fields + [
        ('names', alias, ZERO_OR_MORE),
    ]


class ImportFrom(stmt):
    _fields = stmt._fields + [
        ('module', identifier, OPTIONAL),
        ('names', alias, ZERO_OR_MORE),
        ('level', int, OPTIONAL),
    ]


class Global(stmt):
    _fields = stmt._fields + [
        ('names', identifier, ZERO_OR_MORE),
    ]


class Nonlocal(stmt):
    _fields = stmt._fields + [
        ('names', identifier, ZERO_OR_MORE),
    ]


class Expr(stmt):
    _fields = stmt._fields + [
        ('value', expr, NEEDED),
    ]


class Pass(stmt):
    _fields = stmt._fields


class Break(stmt):
    _fields = stmt._fields


class Continue(stmt):
    _fields = stmt._fields


class BoolOp(expr):
    _fields = expr._fields + [
        ('op', boolop, NEEDED),
        ('values', expr, ZERO_OR_MORE),
    ]


class BinOp(expr):
    _fields = expr._fields + [
        ('left', expr, NEEDED),
        ('op', operator, NEEDED),
        ('right', expr, NEEDED),
    ]


class UnaryOp(expr):
    _fields = expr._fields + [
        ('op', unaryop, NEEDED),
        ('operand', expr, NEEDED),
    ]


class Lambda(expr):
    _fields = expr._fields + [
        ('args', arguments, NEEDED),
        ('body', expr, NEEDED),
    ]


class IfExp(expr):
    _fields = expr._fields + [
        ('test', expr, NEEDED),
        ('body', expr, NEEDED),
        ('orelse', expr, NEEDED),
    ]


class Dict(expr):
    _fields = expr._fields + [
        ('keys', expr, ZERO_OR_MORE),
        ('values', expr, ZERO_OR_MORE),
    ]


class Set(expr):
    _fields = expr._fields + [
        ('elts', expr, ZERO_OR_MORE),
    ]


class ListComp(expr):
    _fields = expr._fields + [
        ('elt', expr, NEEDED),
        ('generators', comprehension, ZERO_OR_MORE),
    ]


class SetComp(expr):
    _fields = expr._fields + [
        ('elt', expr, NEEDED),
        ('generators', comprehension, ZERO_OR_MORE),
    ]


class DictComp(expr):
    _fields = expr._fields + [
        ('key', expr, NEEDED),
        ('value', expr, NEEDED),
        ('generators', comprehension, ZERO_OR_MORE),
    ]


class GeneratorExp(expr):
    _fields = expr._fields + [
        ('elt', expr, NEEDED),
        ('generators', comprehension, ZERO_OR_MORE),
    ]


class Yield(expr):
    _fields = expr._fields + [
        ('value', expr, OPTIONAL),
    ]


class YieldFrom(expr):
    _fields = expr._fields + [
        ('value', expr, NEEDED),
    ]


class Compare(expr):
    _fields = expr._fields + [
        ('left', expr, NEEDED),
        ('ops', cmpop, ZERO_OR_MORE),
        ('comparators', expr, ZERO_OR_MORE),
    ]


class Call(expr):
    _fields = expr._fields + [
        ('func', expr, NEEDED),
        ('args', expr, ZERO_OR_MORE),
        ('keywords', keyword, ZERO_OR_MORE),
        ('starargs', expr, OPTIONAL),
        ('kwargs', expr, OPTIONAL),
    ]


class Attribute(expr):
    _fields = expr._fields + [
        ('value', expr, NEEDED),
        ('attr', identifier, NEEDED),
        ('ctx', expr_context, NEEDED),
    ]


class Subscript(expr):
    _fields = expr._fields + [
        ('value', expr, NEEDED),
        ('slice', slice, NEEDED),
        ('ctx', expr_context, NEEDED),
    ]


class Starred(expr):
    _fields = expr._fields + [
        ('value', expr, NEEDED),
        ('ctx', expr_context, NEEDED),
    ]


class Name(expr):
    _fields = expr._fields + [
        ('id', identifier, NEEDED),
        ('ctx', expr_context, NEEDED),
    ]


class List(expr):
    _fields = expr._fields + [
        ('elts', expr, ZERO_OR_MORE),
        ('ctx', expr_context, NEEDED),
    ]


class Tuple(expr):
    _fields = expr._fields + [
        ('elts', expr, ZERO_OR_MORE),
        ('ctx', expr_context, NEEDED),
    ]


class Ellipsis(expr):
    _fields = expr._fields


class literal(expr):
    _fields = expr._fields


class Str(literal):
    _fields = literal._fields + [
        ('s', str, NEEDED),
    ]


class Bytes(literal):
    _fields = literal._fields + [
        ('s', bytes, NEEDED),
    ]


class Bool(literal):
    _fields = literal._fields + [
        ('b', bool, NEEDED),
    ]


class num(literal):
    _fields = literal._fields


class Int(num):
    _fields = num._fields + [
        ('n', int, NEEDED),
    ]


class Float(num):
    _fields = num._fields + [
        ('n', float, NEEDED),
    ]


class Complex(num):
    _fields = num._fields + [
        ('n', complex, NEEDED),
    ]


class Load(expr_context):
    _fields = expr_context._fields


class Store(expr_context):
    _fields = expr_context._fields


class Del(expr_context):
    _fields = expr_context._fields


class AugLoad(expr_context):
    _fields = expr_context._fields


class AugStore(expr_context):
    _fields = expr_context._fields


class Param(expr_context):
    _fields = expr_context._fields


class Slice(slice):
    _fields = slice._fields + [
        ('lower', expr, OPTIONAL),
        ('upper', expr, OPTIONAL),
        ('step', expr, OPTIONAL),
    ]


class ExtSlice(slice):
    _fields = slice._fields + [
        ('dims', slice, ZERO_OR_MORE),
    ]


class Index(slice):
    _fields = slice._fields + [
        ('value', expr, NEEDED),
    ]


class And(boolop):
    _fields = boolop._fields


class Or(boolop):
    _fields = boolop._fields


class Add(operator):
    _fields = operator._fields


class Sub(operator):
    _fields = operator._fields


class Mult(operator):
    _fields = operator._fields


class Div(operator):
    _fields = operator._fields


class Mod(operator):
    _fields = operator._fields


class Pow(operator):
    _fields = operator._fields


class LShift(operator):
    _fields = operator._fields


class RShift(operator):
    _fields = operator._fields


class BitOr(operator):
    _fields = operator._fields


class BitXor(operator):
    _fields = operator._fields


class BitAnd(operator):
    _fields = operator._fields


class FloorDiv(operator):
    _fields = operator._fields


class Invert(unaryop):
    _fields = unaryop._fields


class Not(unaryop):
    _fields = unaryop._fields


class UAdd(unaryop):
    _fields = unaryop._fields


class USub(unaryop):
    _fields = unaryop._fields


class Eq(cmpop):
    _fields = cmpop._fields


class NotEq(cmpop):
    _fields = cmpop._fields


class Lt(cmpop):
    _fields = cmpop._fields


class LtE(cmpop):
    _fields = cmpop._fields


class Gt(cmpop):
    _fields = cmpop._fields


class GtE(cmpop):
    _fields = cmpop._fields


class Is(cmpop):
    _fields = cmpop._fields


class IsNot(cmpop):
    _fields = cmpop._fields


class In(cmpop):
    _fields = cmpop._fields


class NotIn(cmpop):
    _fields = cmpop._fields
