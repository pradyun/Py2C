#!/usr/bin/env python
import sys
import random
import unittest

import support

from py2c import dual_ast
from py2c.translator import PythonTranslator, TranslationError


class ErrorReportingTestCase(unittest.TestCase):
    """Tests for Error Reporting in PythonTranslator"""
    def setUp(self):
        self.translator = PythonTranslator()

    def template(self, errors):
        for err in errors:
            self.translator.log_error(*err)

        with self.assertRaises(TranslationError) as obj:
            self.translator.handle_errors()

        return obj.exception.errors

    def test_initial_errors(self):
        try:
            self.translator.handle_errors()
        except:
            self.fail("Raised error unexpectedly")

    def test_logging_one_error(self):
        self.translator.log_error("foo")

        with self.assertRaises(TranslationError) as obj:
            self.translator.handle_errors()

        self.assertIn("foo", obj.exception.errors)

    def test_logging_error_with_node(self):
        num = random.randint(1, 2000)
        mock = support.mock.Mock()
        mock.lineno = num

        self.translator.log_error("foo", mock)

        with self.assertRaises(TranslationError) as obj:
            self.translator.handle_errors()

        errors = obj.exception.errors

        err_msg = errors[0]
        self.assertIn("foo", err_msg)
        self.assertIn("line", err_msg.lower())
        self.assertIn(str(num), err_msg)


class CodeTestCase(unittest.TestCase):
    """Base for Python code to AST translation
    """
    longMessage = True  # useful!

    def template(self, tests, remove_expr=False):
        failed = []
        for code, expected in tests:
            result = self.translator.get_node(code).body
            # Remove the code from Expr
            if remove_expr and len(result) == 1:
                result = result[0].value

            if expected != result:
                failed.append(code)

        if failed:
            self.fail(
                "Incorrect values returned for {0}".format(
                    # Failed code in quotes
                    ", ".join(map(repr, failed)))
            )

    def setUp(self):
        self.translator = PythonTranslator()


class LiteralTestCase(CodeTestCase):
    def test_num(self):
        self.template([
            ### Integers
            # Binary integers
            ("0b100110111", dual_ast.Binary("0b100110111")),
            # Decimal integers
            ("3", dual_ast.Int(3)),
            ("7", dual_ast.Int(7)),
            ("2147483647", dual_ast.Int(2147483647)),
            ("79228162514", dual_ast.Int(79228162514)),
            # Octal integers
            ("0o177", dual_ast.Octal("0o177")),
            ("0o377", dual_ast.Octal("0o377")),
            # Hexadecimal integers
            ("0x100000000", dual_ast.Hex("0x100000000")),
            ("0xdeadbeef", dual_ast.Hex("0xdeadbeef")),

            ### Floats
            ("3.14", dual_ast.Float(3.14)),
            ("10.", dual_ast.Float(10.)),
            (".001", dual_ast.Float(.001)),
            ("1e100", dual_ast.Float(1e100)),
            ("3.14e-10", dual_ast.Float(3.14e-10)),
            ("0e0", dual_ast.Float(0e0)),

            ### Complex
            ("3.14j", dual_ast.Complex(3.14j)),
            ("10.j", dual_ast.Complex(10.j)),
            ("10j", dual_ast.Complex(10j)),
            (".001j", dual_ast.Complex(.001j)),
            ("1e100j", dual_ast.Complex(1e100j)),
            ("3.14e-10j", dual_ast.Complex(3.14e-10j)),
        ], remove_expr=True)

    def test_str(self):
        self.template([
            ('"abc"', dual_ast.Str("abc")),
            ('"abc"', dual_ast.Str("abc")),
            ("'''abc'''", dual_ast.Str("abc")),
            ('"""abc"""', dual_ast.Str("abc")),
            (r'r"a\bc"', dual_ast.Str(r"a\bc")),
        ], remove_expr=True)


class StmtTestCase(CodeTestCase):
    """Tests for statements
    """
    @unittest.skipUnless(sys.version_info[0] < 3, "Need Python 2")
    def test_print(self):
        self.template([
            ("print 'x'", dual_ast.Print(
                dest=None,
                sep=" ",
                end="\n",
                values=[dual_ast.Str("x")],
            )),
            ("print >> foo, 'x'", dual_ast.Print(
                dest=dual_ast.Name("foo"),
                sep=" ",
                end="\n",
                values=[dual_ast.Str("x")],
            )),
            ("print 'x',", dual_ast.Print(
                dest=None,
                sep=" ",
                end=" ",
                values=[dual_ast.Str("x")],
            )),
            ("print 'x', 'y'", dual_ast.Print(
                dest=None,
                sep=" ",
                end="\n",
                values=[dual_ast.Str("x"), dual_ast.Str("y")],
            )),
            ("print", dual_ast.Print(
                dest=None,
                sep=" ",
                end="\n",
                values=[],
            )),
            ("print >> foo", dual_ast.Print(
                dest=dual_ast.Name("foo"),
                sep=" ",
                end="\n",
                values=[dual_ast.Str("x")],
            )),
        ])

    def test_assert(self):
        self.template([
            ("assert False", dual_ast.Assert(dual_ast.name(False))),
        ])

    def test_assign(self):
        self.template([
            ("a = b", dual_ast.Assign(
                targets=[dual_ast.Name("a")],
                value=dual_ast.Name("b"),
            )),
            ("a = b = c", dual_ast.Assign(
                targets=[dual_ast.Name("a"), dual_ast.Name("b")],
                value=dual_ast.Name("c"),
            )),
        ])

# TODO: More tests for the same.

if __name__ == '__main__':
    unittest.main()
