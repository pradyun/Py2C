"""Tests for the Python -> AST translator
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import ast
import random
import textwrap

from py2c.ast import python
from py2c.pre_processing.to_ast import PythonToAST, TranslationError

from py2c.tests import Test
from nose.tools import assert_equal, assert_raises, assert_in


# TODO: Refactor to_ast.py to use 'logging' module.
# XXX: Depends on implementation detail
class TestErrorReporting(Test):
    """Tests for error reporting for PythonToAST
    """

    def test_no_errors(self):
        """Make sure the initial state of the Translator doesn't have errors
        """
        translator = PythonToAST()
        try:
            translator._handle_errors()
        except TranslationError:
            self.fail("Raised error unexpectedly")

    def test_invalid_code_input(self):
        with assert_raises(TranslationError) as obj:
            PythonToAST().convert("$$$")

        err = obj.exception
        assert_in("invalid", err.args[0].lower())
        assert_in("code", err.args[0].lower())

    def check_error_reporter(self, errors, required_phrases):
        translator = PythonToAST()
        for err in errors:
            translator._log_error(*err)

        with assert_raises(TranslationError) as context:
            translator._handle_errors()

        for msg, logged_msg in zip(required_phrases, context.exception.errors):
            for part in msg:
                assert_in(part, logged_msg)

    def test_error_reporter(self):
        line_no = random.randint(1, 2000)
        yield from self.yield_tests(self.check_error_reporter, [
            ([("foobar", None)], [["foo"]]),
            # XXX: Case sensitive
            ([("foobar", line_no)], [["foo", "Line", str(line_no)]])
        ])


class TestTranslationError(Test):
    """Tests for TranslationError's attribute handling
    """

    def check_initialization(self, args, kwargs, msg, errors):
        err = TranslationError(*args, **kwargs)
        assert_equal(err.msg, msg)
        assert_equal(err.errors, errors)

    def test_initialization(self):
        yield from self.yield_tests(self.check_initialization, [
            ([], {}, "", None),
            (["Foo"], {}, "Foo", None),
            (["Foo", 1], {}, "Foo", 1),
            ([], {"errors": 1}, "", 1),
        ])


class CodeTest(Test):
    """Base for Python code to AST translation
    """

    def check_code_translation(self, code, expected):
        processed_code = self.process_code(code)
        node = PythonToAST().convert(processed_code)
        result = self.process_node(node)

        if not result:
            result = None
        elif len(result) == 1:
            result = result[0]

        # Remove Expr node if it is the parent node.
        if isinstance(result, python.Expr):
            result = result.value

        assert_equal(expected, result)

    def process_code(self, code):
        """Process the input code before translation.
        """
        return textwrap.dedent(code)

    def process_node(self, node):
        """Process the result of translation before comparision.
        """
        # node.finalize()
        return node.body


class TestLiterals(CodeTest):
    """Tests for literals
    """

    # XXX: Uses implementation details
    def test_invalid_number(self):
        node = ast.Num("string!!")

        translator = PythonToAST()
        translator._visit(node)
        with assert_raises(TranslationError) as context:
            translator._handle_errors()
        errors = context.exception.errors
        assert_equal(len(errors), 1)

    def test_int(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, python.Int(eval(s))) for s in (
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
            )
        ])

    def test_float(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, python.Float(eval(s))) for s in (
                "3.14",
                "10.",
                ".001",
                "1e100",
                "3.14e-10",
                "0e0",
            )
        ])

    def test_complex(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, python.Complex(eval(s))) for s in (
                "10j",
                ".001j",
                "3.14e-10j",
                "3.14j",
                "1e100j",
                "10.j",
            )
        ])

    def test_str(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, python.Str(eval(s))) for s in (
                '"abc"',
                '"abc"',
                "'''abc'''",
                '"""abc"""',
                r'r"a\bc"',
            )
        ])

    def test_nameconstant(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, python.NameConstant(eval(s))) for s in (
                "None",
                "True",
                "False",
            )
        ])


class TestSimpleStatement(CodeTest):
    """Tests for simple statements
    """

    def test_assert(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("assert False", python.Assert(
                python.NameConstant(False), None
            )),
            ("assert False, msg", python.Assert(
                python.NameConstant(False),
                python.Name("msg", python.Load()),
            )),
        ])

    def test_assign(self):
        yield from self.yield_tests(self.check_code_translation, [
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

    def test_delete(self):
        yield from self.yield_tests(self.check_code_translation, [
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
        yield from self.yield_tests(self.check_code_translation, [
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
        yield from self.yield_tests(self.check_code_translation, [
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
        yield from self.yield_tests(self.check_code_translation, [
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
        yield from self.yield_tests(self.check_code_translation, [
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
        yield from self.yield_tests(self.check_code_translation, [
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


class TestCompoundStatement(CodeTest):
    """Tests for statements containing other statements
    """

    def test_if(self):
        yield from self.yield_tests(self.check_code_translation, [
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

    def test_try(self):
        yield from self.yield_tests(self.check_code_translation, [
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
        yield from self.yield_tests(self.check_code_translation, [
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


class TestsCompoundStatementPart(CodeTest):
    """Tests for statements that can only be part of compound statements
    """

    def process_node(self, node):
        return node.body[0].body

    def test_while(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("while True:\n pass", python.Pass()),
            ("while True:\n break", python.Break()),
            ("while True:\n continue", python.Continue()),
        ])

    def test_for(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("for val in iter:\n pass", python.Pass()),
            ("for val in iter:\n break", python.Break()),
            ("for val in iter:\n continue", python.Continue()),
        ])

    def test_function_parts(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("def foo():\n pass", python.Pass()),
            ("def foo():\n global a", python.Global(['a'])),
            ("def foo():\n global a, b", python.Global(['a', "b"])),
            ("def foo():\n nonlocal a", python.Nonlocal(['a'])),
            ("def foo():\n nonlocal a, b", python.Nonlocal(['a', "b"])),
        ])


if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
