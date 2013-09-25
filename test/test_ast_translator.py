#!/usr/bin/env python

import ast
import unittest

import support

with support.project_imports():
    import py2c
    import c_ast

c_ast.prepare()


class ASTTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for C AST translation"""
    longMessage = True # useful!

    def template(self, py_node, check_node, msg=""):
        """The template for tests in `ASTTestCase`s"""
        msg = "Improper conversion" + (" of {0}".format(msg) if msg else '')
        c_node = self.get_c_ast(py_node)
        self.assertEqual(c_node, check_node, msg=msg)

    def setUp(self):
        self.translator = py2c.ASTTranslator()

    def get_c_ast(self, py_node):
        self.node = py_node
        return self.translator.visit(self.node)


class NumTestCase(ASTTestCase):

    """Tests for translation from Num"""
    def test_int_negative(self):
        self.template(ast.Num(-1), c_ast.Int(-1), "-ve integer")

    def test_int_positive(self):
        self.template(ast.Num(1), c_ast.Int(1), "+ve integer")

    def test_int_zero(self):
        self.template(ast.Num(0), c_ast.Int(0), "0 (int)")

    def test_float_negative(self):
        self.template(ast.Num(-1.0), c_ast.Float(-1.0), "-ve float")

    def test_float_positive(self):
        self.template(ast.Num(1.0), c_ast.Float(1.0), "+ve float")

    def test_float_zero(self):
        self.template(ast.Num(0.0), c_ast.Float(0.0), "0 (float)")


class StrTestCase(ASTTestCase):
    """Tests for translation from Str"""

    def test_string(self):
        self.template(ast.Str("abc"), c_ast.Str("abc"))


class Print2TestCase(ASTTestCase):
    """Tests for translation from Print (Python 2)"""

    def test_py2_print1(self):
        """Empty print"""
        self.template(ast.Print(values=[], dest=None, nl=True),
            c_ast.Print(values=[], dest=None, sep=' ', end='\n'))

    def test_py2_print2(self):
        """Empty print with dest"""
        self.template(ast.Print(values=[], dest=ast.Name(id="foo"), nl=True),
            c_ast.Print(values=[], dest=c_ast.Name(id="foo"), sep=' ', end='\n')
        )

    def test_py2_print3(self):
        """Empty print with no newline"""
        self.template(ast.Print(values=[], dest=ast.Name(id="foo"), nl=False),
            c_ast.Print(values=[], dest=c_ast.Name(id="foo"), sep=' ', end=' ')
        )

    def test_py2_print4(self):
        """Print with values, dest but no newline"""
        self.template(ast.Print(values=[ast.Name(id="foo")], dest=ast.Name(id="bar"),
                                nl=False),
            c_ast.Print(values=[c_ast.Name(id="foo")], dest=c_ast.Name(id="bar"),
                        sep=' ', end=' ')
            )

    def test_py2_print5(self):
        """Print with values, dest, newline"""
        self.template(ast.Print(values=[ast.Name(id="foo")],
                                dest=ast.Name(id="bar"), nl=True),
            c_ast.Print(values=[c_ast.Name(id="foo")], dest=c_ast.Name(id="bar"),
                        sep=' ', end='\n')
            )

    def test_py2_print6(self):
        """Print with values, no dest or newline"""
        self.template(ast.Print(values=[ast.Name(id="foo")], dest=None, nl=False),
            c_ast.Print(values=[c_ast.Name(id="foo")], dest=None, sep=' ', end=' ')
        )


class Print3TestCase(ASTTestCase):
    """Tests for translation from Print (Python 3)"""

    def test_py3_print1(self):
        """Empty print"""
        # print()
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[], keywords=[],
                starargs=None, kwargs=None
            ),
            c_ast.Print(values=[], dest=None, sep=' ', end='\n')
        )

    def test_py3_print2(self):
        """Empty print with out-file"""
        # print(file=foo)
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[],
                     keywords=[ast.keyword(arg='file', value=ast.Name(id="foo"))],
                     starargs=None, kwargs=None
            ),
            c_ast.Print(values=[], dest=c_ast.Name(id="foo"), sep=' ', end='\n')
        )

    def test_py3_print3(self):
        """Empty print with no newline"""
        # print(end='')
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[],
                keywords=[ast.keyword(arg='end', value=ast.Str(s=''))],
                starargs=None, kwargs=None
            ),
            c_ast.Print(values=[], dest=None, sep=' ', end='')
        )

    def test_py3_print4(self):
        """Print with file but no end or value"""
        # print(file=foo, end="")
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[],
                keywords=[ast.keyword(arg='file', value=ast.Name(id='foo')),
                          ast.keyword(arg='end',  value=ast.Str(s=''))],
                starargs=None, kwargs=None
            ),
            c_ast.Print(values=[], dest=c_ast.Name(id="foo"),
                        sep=' ', end='')
        )

    def test_py3_print5(self):
        """Print with values, dest but no newline"""
        # print(foo, file=bar)
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[ast.Name(id='foo')],
                keywords=[ast.keyword(arg='file', value=ast.Name(id='bar')),
                          ast.keyword(arg='end', value=ast.Str(s=''))],
                starargs=None, kwargs=None
            ),
            c_ast.Print(values=[c_ast.Name(id="foo")], dest=c_ast.Name(id="bar"),
                        sep=' ', end='')
        )

    def test_py3_print6(self):
        """Print with values, dest, newline"""
        # print(foo, file=bar, end='')
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[ast.Name(id='foo')],
                keywords=[ast.keyword(arg='file', value=ast.Name(id='bar')),
                          ast.keyword(arg='end', value=ast.Str(s=''))],
                starargs=None, kwargs=None
            ),
            c_ast.Print(values=[c_ast.Name(id="foo")], dest=c_ast.Name(id="bar"),
                        sep=' ', end='')
        )

    def test_py3_print7(self):
        """Print with values, no dest or newline"""
        # print(foo, end="")
        self.template(
            ast.Call(func=ast.Name(id='print'), args=[ast.Name(id='foo')],
                keywords=[ast.keyword(arg='end', value=ast.Str(s=''))],
                starargs=None, kwargs=None
            ),
            c_ast.Print(values=[c_ast.Name(id="foo")], dest=None, sep=' ', end='')
        )

if __name__ == '__main__':
    unittest.main()
