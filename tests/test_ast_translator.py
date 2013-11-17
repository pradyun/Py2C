#!/usr/bin/env python

import sys
import ast
import random
import unittest
import contextlib

import support

import py2c.ast_translator as ast_translator
dual_ast = ast_translator.dual_ast


class NodeTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for C AST translation"""
    longMessage = True  # useful!

    def template(self, py_node, expected, msg=""):
        """The template for tests in `NodeTestCase`s"""
        msg = "Improper conversion" + (" of {0}".format(msg) if msg else '')
        c_node = self.get_c_ast(py_node)
        self.assertEqual(c_node, expected, msg=msg)

    def setUp(self):
        self.translator = ast_translator.Py2DualTranslator()

    def get_c_ast(self, py_node):
        self.node = py_node
        return self.translator.visit(self.node)


class ErrorReportingTestCase(unittest.TestCase):
    """Tests for Error Reporting in Py2DualTranslator"""
    def setUp(self):
        self.translator = ast_translator.Py2DualTranslator()

    @contextlib.contextmanager
    def patch_stdout(self):
        # Redirect sys.stdout
        new = support.StringIO()
        old = sys.stdout
        sys.stdout = new
        yield new

        sys.stdout = old

    def test_initial_errors(self):
        self.assertFalse(self.translator.errors)

    def test_logging_one_error(self):
        self.translator.log_error("foo")
        self.assertTrue(self.translator.errors)
        self.assertIn("foo", self.translator.errors)

    def test_printing_one_error(self):
        self.translator.log_error("foo")
        self.assertTrue(self.translator.errors)

        with self.patch_stdout() as output:
            self.translator.print_errors()

        output = output.getvalue()

        # Should mention the following words
        words = ["error", "translating", "ast"]
        for word in words:
            self.assertIn(word, output.lower())

        self.assertEqual(len(output.splitlines()), 1+1)

    def test_printing_no_error(self):
        self.assertFalse(self.translator.errors)

        with self.patch_stdout() as output:
            self.translator.print_errors()

        self.assertEqual(output.getvalue(), "")

    def test_logging_error_with_node(self):
        num = random.randint(10, 200)
        mock = support.mock.Mock()
        mock.lineno = num

        self.translator.log_error("foo", mock)
        self.assertTrue(self.translator.errors)
        err_msg = self.translator.errors[0]
        self.assertIn("foo", err_msg)
        self.assertIn("line", err_msg.lower())
        self.assertIn(str(num), err_msg)

    def test_get_node_no_errors(self):
        # Monkey patch so it does nothing
        self.translator.visit = lambda x: x
        with self.patch_stdout() as output:
            self.translator.get_node("foo")
        self.assertFalse(output.getvalue())

    def test_get_node_with_errors(self):
        msg = "Some problem took place"
        # Monkey patch so it does nothing
        self.translator.visit = lambda x: self.translator.log_error(msg)

        with self.patch_stdout() as output:
            self.translator.get_node("foo")
        output = output.getvalue()

        self.assertTrue(output)
        self.assertIn(msg, output)
        # Male case-insensitive matches
        output = output.lower()
        # Make sure the error message is informative
        self.assertIn("error(s)", output)
        self.assertIn("occurred", output)
        self.assertIn("translating", output)
        self.assertIn("python", output)
        self.assertIn("ast", output)
        self.assertIn("dual", output)


#--------------------------------------------------------------------------
# Tests for each Node
#--------------------------------------------------------------------------
class NumTestCase(NodeTestCase):
    """Tests for translation from Num"""

    def test_int_negative(self):
        self.template(ast.Num(-1), dual_ast.Int(-1), "-ve integer")

    def test_int_positive(self):
        self.template(ast.Num(1), dual_ast.Int(1), "+ve integer")

    def test_int_zero(self):
        self.template(ast.Num(0), dual_ast.Int(0), "0 (int)")

    def test_float_negative(self):
        self.template(ast.Num(-1.0), dual_ast.Float(-1.0), "-ve float")

    def test_float_positive(self):
        self.template(ast.Num(1.0), dual_ast.Float(1.0), "+ve float")

    def test_float_zero(self):
        self.template(ast.Num(0.0), dual_ast.Float(0.0), "0 (float)")

    def test_other(self):
        self.template(ast.Num(0j), None)
        self.assertTrue(self.translator.errors)


class StrTestCase(NodeTestCase):
    """Tests for translation from Str"""

    def test_string(self):
        self.template(ast.Str("abc"), dual_ast.Str("abc"))


# TODO : refector names
@unittest.skipUnless(sys.version_info[0] < 3, "Need Python 2 to run")
class Print2TestCase(NodeTestCase):
    """Tests for translation from Print (Python 2)"""

    def test_py2_print1(self):
        """Empty print"""
        # print
        self.template(
            ast.Print(
                values=[],
                dest=None,
                nl=True
            ),
            dual_ast.Print(
                values=[],
                dest=None,
                sep=' ',
                end='\n'
            )
        )

    def test_py2_print2(self):
        """Empty print with dest"""
        # print >>foo
        self.template(
            ast.Print(
                values=[],
                dest=ast.Name(id="foo", ctx=ast.Load()),
                nl=True
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                sep=' ',
                end='\n'
            )
        )

    def test_py2_print3(self):
        """Empty print with no newline"""
        # print >> foo,
        self.template(
            ast.Print(
                values=[],
                dest=ast.Name(id="foo", ctx=ast.Load()),
                nl=False
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                sep=' ',
                end=' '
            )
        )

    def test_py2_print4(self):
        """Print with values, dest but no newline"""
        # print >>bar, foo,
        self.template(
            ast.Print(
                values=[ast.Name(id="foo", ctx=ast.Load())],
                dest=ast.Name(id="bar", ctx=ast.Load()),
                nl=False
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                sep=' ',
                end=' '
            )
        )

    def test_py2_print5(self):
        """Print with values, dest, newline"""
        # print >>bar, foo
        self.template(
            ast.Print(
                values=[ast.Name(id="foo", ctx=ast.Load())],
                dest=ast.Name(id="bar", ctx=ast.Load()),
                nl=True
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                sep=' ',
                end='\n'
            )
        )

    def test_py2_print6(self):
        """Print with values, no dest or newline"""
        # print foo,
        self.template(
            ast.Print(
                values=[ast.Name(id="foo", ctx=ast.Load())],
                dest=None,
                nl=False
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=None,
                sep=' ',
                end=' '
            )
        )

    def test_py2_print7(self):
        """Print with values and newline but no dest"""
        # print foo
        self.template(
            ast.Print(
                values=[ast.Name(id="foo", ctx=ast.Load())],
                dest=None,
                nl=True
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=None,
                sep=' ',
                end='\n'
            )
        )


class Print3TestCase(NodeTestCase):
    """Tests for translation from Print (Python 3)"""

    def test_py3_print_empty(self):
        """Empty print"""
        # print()
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=None,
                sep=' ',
                end='\n'
            )
        )

    def test_py3_print_dest(self):
        """Empty print with out-file"""
        # print(file=foo)
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id="foo", ctx=ast.Load()))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                sep=' ',
                end='\n'
            )
        )

    def test_py3_print_no_nl(self):
        """Empty print with no newline"""
        # print(end='')
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg='end', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=None,
                sep=' ',
                end=''
            )
        )

    def test_py3_print_dest_no_nl(self):
        """Print with file but no end or value"""
        # print(file=foo, end='')
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id="foo", ctx=ast.Load())),
                    ast.keyword(arg='end',  value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[],
                dest=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                sep=' ',
                end=''
            )
        )

    def test_py3_print_value_dest_no_nl(self):
        """Print with values, dest but no newline"""
        # print(foo, file=bar, end='')
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[ast.Name(id="foo", ctx=ast.Load())],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id="bar", ctx=ast.Load())),
                    ast.keyword(arg='end', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                sep=' ',
                end=''
            )
        )

    def test_py3_print_value_dest_nl(self):
        """Print with values, dest, newline"""
        # print(foo, file=bar)
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[ast.Name(id="foo", ctx=ast.Load())],
                keywords=[
                    ast.keyword(arg='file', value=ast.Name(id="bar", ctx=ast.Load()))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                sep=' ',
                end='\n'
            )
        )

    def test_py3_print_value_only(self):
        """Print with values, no dest or newline"""
        # print(foo, end='')
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[ast.Name(id="foo", ctx=ast.Load())],
                keywords=[
                    ast.keyword(arg='end', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Print(
                values=[dual_ast.Name(id="foo", ctx=dual_ast.Load())],
                dest=None,
                sep=' ',
                end=''
            )
        )

    def test_py3_print_unexpected_kwd(self):
        """Print with unexpected keyword"""
        # print(foo, incorrect_kwd='')
        self.template(
            ast.Call(
                func=ast.Name(id="print", ctx=ast.Load()),
                args=[ast.Name(id="foo", ctx=ast.Load())],
                keywords=[
                    ast.keyword(arg='incorrect_kwd', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            None
        )
        self.assertTrue(self.translator.errors)


class CallTestCase(NodeTestCase):
    """Tests for translation of Call"""
    def test_call_no_args(self):
        # foo()
        self.template(
            ast.Call(
                func=ast.Name(id="foo", ctx=ast.Load()),
                args=[],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Call(
                func=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                args=[]
            )
        )

    def test_call_1_arg(self):
        # foo(bar)
        self.template(
            ast.Call(
                func=ast.Name(id="foo", ctx=ast.Load()),
                args=[ast.Name(id="bar", ctx=ast.Load())],
                keywords=[],
                starargs=None,
                kwargs=None
            ),
            dual_ast.Call(
                func=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                args=[dual_ast.Name(id="bar", ctx=dual_ast.Load())]
            )
        )

    def test_call_1_kwd(self):
        # foo(unexpected_kwd='')
        self.template(
            ast.Call(
                func=ast.Name(id="foo", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg='unexpected_kwd', value=ast.Str(s=''))
                ],
                starargs=None,
                kwargs=None
            ),
            None
        )
        self.assertTrue(self.translator.errors)

    def test_call_starred(self):
        # foo(*starred)
        self.template(
            ast.Call(
                func=ast.Name(id="foo", ctx=ast.Load()),
                args=[],
                keywords=[],
                starargs=ast.Name(id="starred", ctx=ast.Load()),
                kwargs=None
            ),
            None
        )
        self.assertTrue(self.translator.errors)


class BoolOpTestCase(NodeTestCase):
    """Tests for translation from BoolOp"""

    def test_boolop_and1(self):
        self.template(
            ast.BoolOp(
                op=ast.And(),
                values=[
                    ast.Name(id="foo", ctx=ast.Load()),
                    ast.Name(id="bar", ctx=ast.Load())
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.And(),
                values=[
                    dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                    dual_ast.Name(id="bar", ctx=dual_ast.Load())
                ]
            )
        )

    def test_boolop_and2(self):
        self.template(
            ast.BoolOp(
                op=ast.And(),
                values=[
                    ast.Name(id="foo", ctx=ast.Load()),
                    ast.Name(id="bar", ctx=ast.Load()),
                    ast.Name(id="baz", ctx=ast.Load()),
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.And(),
                values=[
                    dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                    dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                    dual_ast.Name(id="baz", ctx=dual_ast.Load()),
                ]
            )
        )

    def test_boolop_or1(self):
        self.template(
            ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.Name(id="foo", ctx=ast.Load()),
                    ast.Name(id="bar", ctx=ast.Load())
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.Or(),
                values=[
                    dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                    dual_ast.Name(id="bar", ctx=dual_ast.Load())
                ]
            )
        )

    def test_boolop_or2(self):
        self.template(
            ast.BoolOp(
                op=ast.Or(),
                values=[
                    ast.Name(id="foo", ctx=ast.Load()),
                    ast.Name(id="bar", ctx=ast.Load()),
                    ast.Name(id="baz", ctx=ast.Load())
                ]
            ),
            dual_ast.BoolOp(
                op=dual_ast.Or(),
                values=[
                    dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                    dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                    dual_ast.Name(id="baz", ctx=dual_ast.Load())
                ]
            )
        )

    def test_binop_invalid_op(self):
        node = ast.BoolOp(
            op='Blah',
            values=[ast.Name(id="foo"), ast.Name(id="bar", ctx=ast.Load())]
        )
        self.assertEqual(self.translator.visit(node), None)


class BinOpTestCase(NodeTestCase):
    """Tests for translation from BinOp"""
    def test_binop_Add(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id="foo", ctx=ast.Load()),
                op=ast.Add(),
                right=ast.Name(id="b", ctx=ast.Load())
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                op=dual_ast.Add(),
                right=dual_ast.Name(id="b", ctx=dual_ast.Load())
            )
        )

    def test_binop_Sub(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id="foo", ctx=ast.Load()),
                op=ast.Sub(),
                right=ast.Name(id="b", ctx=ast.Load())
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                op=dual_ast.Sub(),
                right=dual_ast.Name(id="b", ctx=dual_ast.Load())
            )
        )

    def test_binop_Mult(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id="foo", ctx=ast.Load()),
                op=ast.Mult(),
                right=ast.Name(id="b", ctx=ast.Load())
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                op=dual_ast.Mult(),
                right=dual_ast.Name(id="b", ctx=dual_ast.Load())
            )
        )

    def test_binop_Div(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id="foo", ctx=ast.Load()),
                op=ast.Div(),
                right=ast.Name(id="b", ctx=ast.Load())
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                op=dual_ast.Div(),
                right=dual_ast.Name(id="b", ctx=dual_ast.Load())
            )
        )

    def test_binop_Mod(self):
        self.template(
            ast.BinOp(
                left=ast.Name(id="foo", ctx=ast.Load()),
                op=ast.Mod(),
                right=ast.Name(id="b", ctx=ast.Load())
            ),
            dual_ast.BinOp(
                left=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                op=dual_ast.Mod(),
                right=dual_ast.Name(id="b", ctx=dual_ast.Load())
            )
        )

    def test_binop_invalid_op(self):
        node = ast.BinOp(
            op='Blah',  # Not a valid operator
            left=ast.Name(id="foo", ctx=ast.Load()),
            right=ast.Name(id="bar", ctx=ast.Load())
        )
        self.assertEqual(self.translator.visit(node), None)
        self.assertTrue(self.translator.errors)


class UnaryOpTestCase(NodeTestCase):
    """Tests for translation from UnaryOp"""
    def test_unary_Not(self):
        self.template(
            ast.UnaryOp(
                op=ast.Not(),
                operand=ast.Name(id="foo", ctx=ast.Load())
            ),
            dual_ast.UnaryOp(
                op=dual_ast.Not(),
                operand=dual_ast.Name(id="foo", ctx=dual_ast.Load())
            )
        )

    def test_unary_UAdd(self):
        self.template(
            ast.UnaryOp(
                op=ast.UAdd(),
                operand=ast.Name(id="foo", ctx=ast.Load())
            ),
            dual_ast.UnaryOp(
                op=dual_ast.UAdd(),
                operand=dual_ast.Name(id="foo", ctx=dual_ast.Load())
            )
        )

    def test_unary_USub(self):
        self.template(
            ast.UnaryOp(
                op=ast.USub(),
                operand=ast.Name(id="foo", ctx=ast.Load())
            ),
            dual_ast.UnaryOp(
                op=dual_ast.USub(),
                operand=dual_ast.Name(id="foo", ctx=dual_ast.Load())
            )
        )

    def test_unary_Invert(self):
        self.template(
            ast.UnaryOp(
                op=ast.Invert(),
                operand=ast.Name(id="foo", ctx=ast.Load())
            ),
            dual_ast.UnaryOp(
                op=dual_ast.Invert(),
                operand=dual_ast.Name(id="foo", ctx=dual_ast.Load())
            )
        )

    def test_unary_invalid_op(self):
        node = ast.UnaryOp(
            op='Blah',  # Not a valid operator
            operand=ast.Name(id="foo", ctx=ast.Load())
        )
        self.assertEqual(self.translator.visit(node), None)
        self.assertTrue(self.translator.errors)


class IfExpTestCase(NodeTestCase):
    """Tests for translation from IfExp"""
    def test_ifexp(self):
        self.template(
            ast.IfExp(
                test=ast.Name(id="bar", ctx=ast.Load()),
                body=ast.Name(id="foo", ctx=ast.Load()),
                orelse=ast.Name(id="baz", ctx=ast.Load())
            ),
            dual_ast.IfExp(
                test=dual_ast.Name(id="bar", ctx=dual_ast.Load()),
                body=dual_ast.Name(id="foo", ctx=dual_ast.Load()),
                orelse=dual_ast.Name(id="baz", ctx=dual_ast.Load())
            )
        )


class ModuleTestCase(NodeTestCase):
    """Tests for translation from Module"""
    def test_empty_module(self):
        self.template(
            ast.Module([]),
            dual_ast.Module([])
        )

    def test_not_empty_module(self):
        self.template(
            ast.Module(
                body=[ast.Name(id='foo', ctx=ast.Load())]
            ),
            dual_ast.Module(
                body=[dual_ast.Name(id="foo", ctx=dual_ast.Load())]
            )
        )


class ContextTestCase(NodeTestCase):
    """Tests for translation from expr_context nodes"""
        # Context

    def test_AugLoad(self):
        self.template(ast.AugLoad(), dual_ast.AugLoad())

    def test_AugStore(self):
        self.template(ast.AugStore(), dual_ast.AugStore())

    def test_Del(self):
        self.template(ast.Del(), dual_ast.Del())

    def test_Load(self):
        self.template(ast.Load(), dual_ast.Load())

    def test_Param(self):
        self.template(ast.Param(), dual_ast.Param())

    def test_Store(self):
        self.template(ast.Store(), dual_ast.Store())


if __name__ == '__main__':
    unittest.main()
