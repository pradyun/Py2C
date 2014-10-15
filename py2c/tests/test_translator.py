#!/usr/bin/python3
"""Tests for the Python -> AST translator
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import ast
import random
import textwrap
import unittest

from py2c.syntax_tree import python
from py2c.translator import Python2ASTTranslator, TranslationError


# To be re-written soon...
#------------------------------------------------------------------------------
# Even though most of the stuff works.. These tests are not extensive enough..
# If any one has any ideas how these can be simplified, feel free to open an
# issue at http://github.com/pradyun/Py2C/issues
#------------------------------------------------------------------------------
class ErrorReportingTestCase(unittest.TestCase):
    """Tests for Error Reporting in Python2ASTTranslator
    """

    def setUp(self):
        self.translator = Python2ASTTranslator()

    def template(self, errors):
        for err in errors:
            self.translator.log_error(*err)

        with self.assertRaises(TranslationError) as obj:
            self.translator.handle_errors()

        return obj.exception.errors

    def test_no_errors(self):
        try:
            self.translator.handle_errors()
        except TranslationError:
            self.fail("Raised error unexpectedly")

    def test_logging_one_error(self):
        errors = self.template([("foo", None)])
        self.assertIn("foo", errors)

    def test_logging_error_with_lineno(self):
        num = random.randint(1, 2000)

        errors = self.template([("foo", num)])

        err_msg = errors[0]
        self.assertIn("foo", err_msg)
        self.assertIn("line", err_msg.lower())
        self.assertIn(str(num), err_msg)

        # Make sure there is no duplication
        self.assertTrue(err_msg.count("foo"), 1)

    def test_invalid_code_input(self):
        with self.assertRaises(TranslationError) as obj:
            self.translator.get_node("$$$")

        err = obj.exception
        self.assertIn("invalid", err.args[0].lower())
        self.assertIn("code", err.args[0].lower())


class TranslationErrorTestCase(unittest.TestCase):
    """Tests for TranslationError's attribute handling
    """

    def test_no_args(self):
        err = TranslationError()
        self.assertEqual(err.msg, "")
        self.assertEqual(err.errors, None)

    def test_1_arg(self):
        err = TranslationError("Foo")
        self.assertEqual(err.msg, "Foo")
        self.assertEqual(err.errors, None)

    def test_2_args(self):
        err = TranslationError("Foo", 1)
        self.assertEqual(err.msg, "Foo")
        self.assertEqual(err.errors, 1)

    def test_keyword_args(self):
        err = TranslationError(errors=1)
        self.assertEqual(err.msg, "")
        self.assertEqual(err.errors, 1)


class CodeTestCase(unittest.TestCase):
    """Base for Python code to AST translation
    """
    longMessage = True  # useful!

    def template(self, tests, remove_expr=False):
        failed = []
        for code, expected in tests:
            code = textwrap.dedent(code)
            processed_code = self.process_code(code)
            node = self.translator.get_node(processed_code)
            result = self.process_node(node)

            if not result:
                result = None
            elif len(result) == 1:
                result = result[0]

            # Remove the code from Expr
            if remove_expr and isinstance(result, python.Expr):
                result = result.value

            if expected != result:
                failed.append((code, expected, result))
                # print("Expected:", expected)
                # print("Got     :", result)

        if failed:
            msg_parts = ["Translated something(s) incorrectly:"]
            for code, expected, result in failed:
                msg_parts.append("{!r}".format(code))
                msg_parts.append("    Expected: {}".format(expected))
                msg_parts.append("    Got     : {}".format(result))
                # For an empty line between reports
                msg_parts.append("")

            self.fail("\n".join(msg_parts))

    def setUp(self):
        self.translator = Python2ASTTranslator()

    # Allows addition of boiler-plate to processing (eg. Moving inside a loop)
    def process_node(self, node):
        # node.finalize()
        return node.body

    def process_code(self, code):
        return code


class LiteralTestCase(CodeTestCase):
    """Tests for literals
    """

    def test_int(self):
        tests = [
            # Binary
            "0b100110111",
            # Decimal
            "3",
            "7",
            "2147483647",
            "79228162514",
            # Octal
            "0o177",
            "0o377",
            # Hexadecimal
            "0x100000000",
            "0xdeadbeef",
        ]
        self.template([
            (s, python.Int(eval(s))) for s in tests
        ], remove_expr=True)

    def test_float(self):
        tests = [
            "3.14",
            "10.",
            ".001",
            "1e100",
            "3.14e-10",
            "0e0",
        ]

        self.template([
            (s, python.Float(eval(s))) for s in tests
        ], remove_expr=True)

    def test_complex(self):
        tests = [
            "10j",
            ".001j",
            "3.14e-10j",
            "3.14j",
            "1e100j",
            "10.j",
        ]
        self.template([
            (s, python.Complex(eval(s))) for s in tests
        ], remove_expr=True)

    # XXX: Depends on implementation details
    def test_invalid_number(self):
        node = ast.Num("string!!")

        self.translator._visit(node)
        with self.assertRaises(TranslationError):
            self.translator.handle_errors()

    def test_str(self):
        tests = [
            '"abc"',
            '"abc"',
            "'''abc'''",
            '"""abc"""',
            r'r"a\bc"',
        ]
        self.template(
            [(s, python.Str(eval(s))) for s in tests],
            remove_expr=True
        )

    def test_singleton(self):
        singletons = [None, True, False]
        self.template(
            [(str(obj), python.NameConstant(obj)) for obj in singletons],
            remove_expr=True
        )


class SimpleStmtTestCase(CodeTestCase):
    """Tests for simple statements
    """

    def test_assert(self):
        self.template([
            ("assert False", python.Assert(
                python.NameConstant(False), None
            )),
            ("assert False, msg", python.Assert(
                python.NameConstant(False),
                python.Name("msg", python.Load()),
            )),
        ])

    def test_assign(self):
        # Tests for type-info below..
        self.template([
            ("a = b", python.Assign(
                targets=[python.Name("a", python.Store())],
                value=python.Name("b", python.Load()),
            )),
            ("a = b = c", python.Assign(
                targets=[
                    python.Name("a", python.Store()),
                    python.Name("b", python.Store()),
                ],
                value=python.Name("c", python.Load()),
            )),
        ])

    def test_del(self):
        self.template([
            ("del a", python.Delete(targets=[
                python.Name("a", python.Del()),
            ])),
            ("del a, b", python.Delete(targets=[
                python.Name("a", python.Del()),
                python.Name("b", python.Del()),
            ])),
            ("del (a, b)", python.Delete(targets=[
                python.Tuple([
                    python.Name("a", python.Del()),
                    python.Name("b", python.Del()),
                ], python.Del()),
            ])),
            ("del (a\n, b)", python.Delete(targets=[
                python.Tuple([
                    python.Name("a", python.Del()),
                    python.Name("b", python.Del())
                ], python.Del()),
            ])),
            ("del (a\n, b), c", python.Delete(targets=[
                python.Tuple([
                    python.Name("a", python.Del()),
                    python.Name("b", python.Del())
                ], python.Del()),
                python.Name("c", python.Del()),
            ])),
        ])

    def test_raise(self):
        self.template([
            ("raise", python.Raise(
                None, None
            )),
            ("raise err", python.Raise(
                python.Name("err", python.Load()),
                None
            )),
            ("raise err_1 from err_2", python.Raise(
                python.Name("err_1", python.Load()),
                python.Name("err_2", python.Load()),
            )),
        ])

    def test_import_module(self):
        self.template([
            (  # Single import
                "import apple",
                python.Import([
                    python.alias("apple", None),
                ])
            ),
            (  # Single subpackage import
                "import apple.ball",
                python.Import([
                    python.alias("apple.ball", None),
                ])
            ),
            (  # Single alias import
                "import apple as ball",
                python.Import([
                    python.alias("apple", "ball"),
                ])
            ),
            (  # Multiple imports, 1 alias, 1 simple
                "import apple as ball, cat",
                python.Import([
                    python.alias("apple", "ball"),
                    python.alias("cat", None),
                ])
            ),
            (  # Multiple alias imports
                "import apple as ball, cat as dog",
                python.Import([
                    python.alias("apple", "ball"),
                    python.alias("cat", "dog"),
                ])
            ),
            (  # Multiple alias imports from subpackage
                "import apple.ball as ball, cat as dog",
                python.Import([
                    python.alias("apple.ball", "ball"),
                    python.alias("cat", "dog"),
                ])
            ),
        ])

    def test_from_module_import_star(self):
        self.template([
            (
                "from apple import *",
                python.ImportFrom(
                    "apple", [
                        python.alias("*", None)
                    ],
                    0
                )
            ),
            (
                "from apple.ball import *",
                python.ImportFrom(
                    "apple.ball", [
                        python.alias("*", None)
                    ],
                    0
                )
            ),
        ])

    def test_from_module_import_names(self):
        self.template([
            (
                "from apple import ball",
                python.ImportFrom(
                    "apple", [
                        python.alias("ball", None)
                    ],
                    0
                )
            ),
            (
                "from apple import ball as cat",
                python.ImportFrom(
                    "apple", [
                        python.alias("ball", "cat")
                    ],
                    0
                )
            ),
        ])

    def test_from_submodule_import_names(self):
        self.template([
            (
                "from apple.ball import (\n    cat, \n    dog,)",
                python.ImportFrom(
                    "apple.ball",
                    [
                        python.alias("cat", None),
                        python.alias("dog", None),
                    ],
                    0
                )
            ),
            (
                "from apple.ball import cat as dog",
                python.ImportFrom(
                    "apple.ball",
                    [
                        python.alias("cat", "dog")
                    ],
                    0
                )
            ),
            (
                "from apple.ball import cat as dog, egg",
                python.ImportFrom(
                    "apple.ball",
                    [
                        python.alias("cat", "dog"),
                        python.alias("egg", None),
                    ],
                    0
                )
            ),
            (
                "from apple.ball import (\n    cat as dog, \n    egg as frog)",
                python.ImportFrom(
                    "apple.ball",
                    [
                        python.alias("cat", "dog"),
                        python.alias("egg", "frog"),
                    ],
                    0
                )
            ),
        ])

    def test_future_valid(self):
        self.template([
            (
                "from __future__ import with_statement",
                python.Future([
                    python.alias("with_statement", None)
                ])
            ),
            (
                "import __future__ as future",
                python.Import([
                    python.alias("__future__", "future")
                ])
            ),
        ])

    def test_future_invalid(self):
        with self.assertRaises(TranslationError) as obj:
            self.template([
                (
                    "from __future__ import some_wrong_name", None
                )
            ])

        msg = obj.exception.errors[-1]
        self.assertIn("no feature", msg)
        self.assertIn("'some_wrong_name'", msg)


class CompoundStmtTestCase(CodeTestCase):
    """Tests for statements containing other statements
    """

    def test_if(self):
        self.template([
            (
                """
                if True:
                    pass
                """,
                python.If(
                    python.NameConstant(True),
                    [python.Pass()],
                    []
                )
            ),
            (
                """
                if first_cond:
                    first
                elif second_cond:
                    second
                else:
                    third
                """,
                python.If(
                    python.Name(
                        "first_cond", python.Load()
                    ),
                    [python.Expr(
                        python.Name("first", python.Load())
                    )],
                    [
                        python.If(
                            python.Name("second_cond", python.Load()),
                            [python.Expr(
                                python.Name("second", python.Load())
                            )],
                            [python.Expr(
                                python.Name("third", python.Load())
                            )]
                        )
                    ]
                )
            ),

        ])

    def test_while(self):
        self.template([
            (
                "while True: pass",
                python.While(
                    python.NameConstant(True),
                    [python.Pass()],
                    []
                )
            )

        ])

    def test_for(self):
        self.template([
            (
                "for x in li: pass",
                python.For(
                    python.Name("x", python.Store()),
                    python.Name("li", python.Load()),
                    [python.Pass()],
                    []
                )
            )

        ])

    def test_try(self):
        self.template([
            (
                """
                try:
                    pass
                except SomeException as error:
                    pass
                else:
                    pass
                finally:
                    pass
                """,
                python.Try(
                    [python.Pass()],
                    [python.ExceptHandler(
                        python.Name("SomeException", python.Load()),
                        "error",
                        [python.Pass()]
                    )],
                    [python.Pass()],
                    [python.Pass()]
                )
            )
        ])

    def test_with(self):
        self.template([
            (
                """
                with some_context as some_name:
                    pass
                """,
                python.With(
                    [python.withitem(
                        python.Name("some_context", python.Load()),
                        python.Name("some_name", python.Store()),
                    )],
                    [python.Pass()]
                )
            )
        ])

    # TODO: Add tests for classes and functions


class CompoundStmtPartTestCase(CodeTestCase):
    """Tests for statements that can only be part of compound statements
    """

    def process_node(self, node):
        return node.body[0].body

    def process_code(self, code):
        lines = [self.prefix]
        for line in code.splitlines():
            lines.append("    " + line)

        return "\n".join(lines)


class LoopStmtPartTestCase(CompoundStmtPartTestCase):
    """Tests for statements that can be inside loops for flow control
    """

    def test_while(self):
        self.prefix = "while True:"

        self.template([
            ("pass", python.Pass()),
            ("break", python.Break()),
            ("continue", python.Continue()),
        ])

    def test_statements(self):
        self.prefix = "for x in li:"

        self.template([
            ("pass", python.Pass()),
            ("break", python.Break()),
            ("continue", python.Continue()),
        ])


class FunctionStmtPartTestCase(CompoundStmtPartTestCase):
    """Tests for statements that can be inside functions for flow control
    """
    prefix = "def foo():"

    def test_statements(self):
        self.template([
            ("pass", python.Pass()),
            ("global a", python.Global(['a'])),
            ("global a, b", python.Global(['a', "b"])),
            ("nonlocal a", python.Nonlocal(['a'])),
            ("nonlocal a, b", python.Nonlocal(['a', "b"])),
        ])


if __name__ == '__main__':
    unittest.main()
