#!/usr/bin/env python

import sys
import ast
import io
import unittest


import py2c.ast_translator as ast_translator
c_ast = ast_translator.c_ast


class ASTTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for C AST translation"""
    longMessage = True # useful!

    def template(self, py_node, check_node, msg=""):
        """The template for tests in `ASTTestCase`s"""
        msg = "Improper conversion" + (" of {0}".format(msg) if msg else '')
        c_node = self.get_c_ast(py_node)
        self.assertEqual(c_node, check_node, msg=msg)

    def setUp(self):
        self.translator = ast_translator.ASTTranslator()

    def get_c_ast(self, py_node):
        self.node = py_node
        return self.translator.visit(self.node)


class ErrorReportingTestCase(ASTTestCase):
    """Tests for Error Reporting in ASTTranslator"""
    def test_no_error(self):
        node = ast.Module([])
        self.translator.visit(node)
        self.assertFalse(self.translator.errors)
        try:
            self.translator.get_node(node)
        except Exception:
            self.fail("translator.get_node() raised Exception unexpectedly!", )

    def test_logging_one_error(self):
        node = ast.BinOp(
            op='Blah', left=ast.Name(id="foo"), right=ast.Name(id="bar")
        )
        self.translator.visit(node)
        self.assertTrue(self.translator.errors)
        # monkey patch print_error to do nothing
        self.translator.print_errors = lambda : None
        self.translator.get_node(node)

    def test_printing_one_error(self):
        node = ast.BinOp(
            op='Blah', left=ast.Name(id="foo"), right=ast.Name(id="bar")
        )
        self.translator.visit(node)
        self.assertTrue(self.translator.errors)

        # Redirect sys.stdout
        new = io.StringIO()
        old = sys.stdout
        sys.stdout = new

        self.translator.print_errors()
        # restore sys.stdout
        sys.stdout = old
        # get output
        output = new.getvalue()
        new.close()

        self.assertIn("error", output.lower())  # it's an error msg, mention it!
        self.assertIn("ast", output.lower())  # Occured in AST
        self.assertEqual(len(output.splitlines()), 1+1)


#--------------------------------------------------------------------------
# Node by Node tests
#--------------------------------------------------------------------------
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


class BoolOpTestCase(ASTTestCase):
    """Tests for translation from BoolOp"""

    def test_boolop_and1(self):
        self.template(
            ast.BoolOp(op=ast.And(), values=[ast.Name(id='foo'),
                                             ast.Name(id='bar')]
            ),
            c_ast.BoolOp(op=c_ast.And(), values=[c_ast.Name(id='foo'),
                                                 c_ast.Name(id='bar')]
            )
        )

    def test_boolop_and2(self):
        self.template(
            ast.BoolOp(op=ast.And(), values=[ast.Name(id='foo'),
                                             ast.Name(id='bar'),
                                             ast.Name(id='baz')]
            ),
            c_ast.BoolOp(op=c_ast.And(), values=[c_ast.Name(id='foo'),
                                                 c_ast.Name(id='bar'),
                                                 c_ast.Name(id='baz')]
            )
        )

    def test_boolop_or1(self):
        self.template(
            ast.BoolOp(op=ast.Or(), values=[ast.Name(id='foo'),
                                             ast.Name(id='bar')]
            ),
            c_ast.BoolOp(op=c_ast.Or(), values=[c_ast.Name(id='foo'),
                                                 c_ast.Name(id='bar')]
            )
        )

    def test_boolop_or2(self):
        self.template(
            ast.BoolOp(op=ast.Or(), values=[ast.Name(id='foo'),
                                             ast.Name(id='bar'),
                                             ast.Name(id='baz')]
            ),
            c_ast.BoolOp(op=c_ast.Or(), values=[c_ast.Name(id='foo'),
                                                 c_ast.Name(id='bar'),
                                                 c_ast.Name(id='baz')]
            )
        )


class BinOpTestCase(ASTTestCase):
    """Tests for translation from BinOp"""
    def test_binop_Add(self):
        self.template(
            ast.BinOp(left=ast.Name(id='foo'), op=ast.Add(),
                      right=ast.Name(id='b')),
            c_ast.BinOp(left=c_ast.Name(id='foo'), op=c_ast.Add(),
                        right=c_ast.Name(id='b'))
        )

    def test_binop_Sub(self):
        self.template(
            ast.BinOp(left=ast.Name(id='foo'), op=ast.Sub(),
                      right=ast.Name(id='b')),
            c_ast.BinOp(left=c_ast.Name(id='foo'), op=c_ast.Sub(),
                        right=c_ast.Name(id='b'))
        )

    def test_binop_Mult(self):
        self.template(
            ast.BinOp(left=ast.Name(id='foo'), op=ast.Mult(),
                      right=ast.Name(id='b')),
            c_ast.BinOp(left=c_ast.Name(id='foo'), op=c_ast.Mult(),
                        right=c_ast.Name(id='b'))
        )

    def test_binop_Div(self):
        self.template(
            ast.BinOp(left=ast.Name(id='foo'), op=ast.Div(),
                      right=ast.Name(id='b')),
            c_ast.BinOp(left=c_ast.Name(id='foo'), op=c_ast.Div(),
                        right=c_ast.Name(id='b'))
        )

    def test_binop_Mod(self):
        self.template(
            ast.BinOp(left=ast.Name(id='foo'), op=ast.Mod(),
                      right=ast.Name(id='b')),
            c_ast.BinOp(left=c_ast.Name(id='foo'), op=c_ast.Mod(),
                        right=c_ast.Name(id='b'))
        )

    def test_binop_invalid_op(self):
        node = ast.BinOp(
            op='Blah', left=ast.Name(id="foo"), right=ast.Name(id="bar")
        )
        self.assertEqual(self.translator.visit(node), None)


class UnaryOpTestCase(ASTTestCase):
    """Tests for translation from UnaryOp"""
    def test_unary_Not(self):
        self.template(
            ast.UnaryOp(op=ast.Not(), operand=ast.Name(id='foo')),
            c_ast.UnaryOp(op=c_ast.Not(), operand=c_ast.Name(id='foo'))
        )

    def test_unary_And(self):
        self.template(
            ast.UnaryOp(op=ast.And(), operand=ast.Name(id='foo')),
            c_ast.UnaryOp(op=c_ast.And(), operand=c_ast.Name(id='foo'))
        )


class IfExpTestCase(ASTTestCase):
    """Tests for translation from IfExp"""
    def test_ifexp(self):
        self.template(
            ast.IfExp(test=ast.Name(id='bar'), body=ast.Name(id='foo'),
                      orelse=ast.Name(id='baz')),
            c_ast.IfExp(test=c_ast.Name(id='bar'), body=c_ast.Name(id='foo'),
                        orelse=c_ast.Name(id='baz'))
        )


class ModuleTestCase(ASTTestCase):
    """Tests for translation from Module"""
    def test_empty_module(self):
        self.template(ast.Module([]), c_ast.Module([]))

    def test_not_empty_module(self):
        self.template(
            ast.Module(body=[ast.Name(id='foo')]),
            c_ast.Module(body=[c_ast.Name(id="foo")])
        )

if __name__ == '__main__':
    unittest.main()
