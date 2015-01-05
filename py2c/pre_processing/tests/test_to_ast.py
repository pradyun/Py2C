"""Tests for the Python -> AST translator
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import ast
import random
import textwrap

import py2c.tree.python as py_tree
from py2c.pre_processing.to_ast import PythonToAST, TranslationError

from py2c.tests import Test
from nose.tools import assert_equal, assert_raises, assert_in


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
        if isinstance(result, py_tree.Expr):
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
        translator.visit(node)
        with assert_raises(TranslationError) as context:
            translator._handle_errors()
        errors = context.exception.errors
        assert_equal(len(errors), 1)

    def test_int(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, py_tree.Int(eval(s))) for s in (
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
            (s, py_tree.Float(eval(s))) for s in (
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
            (s, py_tree.Complex(eval(s))) for s in (
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
            (s, py_tree.Str(eval(s))) for s in (
                '"abc"',
                '"abc"',
                "'''abc'''",
                '"""abc"""',
                r'r"a\bc"',
            )
        ])

    def test_nameconstant(self):
        yield from self.yield_tests(self.check_code_translation, [
            (s, py_tree.NameConstant(eval(s))) for s in (
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
            ("assert False", py_tree.Assert(
                py_tree.NameConstant(False), None
            )),
            ("assert False, msg", py_tree.Assert(
                py_tree.NameConstant(False),
                py_tree.Name("msg", py_tree.Load()),
            )),
        ])

    def test_assign(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("a = b", py_tree.Assign(
                targets=[py_tree.Name("a", py_tree.Store())],
                value=py_tree.Name("b", py_tree.Load()),
            )),
            ("a = b = c", py_tree.Assign(
                targets=[
                    py_tree.Name("a", py_tree.Store()),
                    py_tree.Name("b", py_tree.Store()),
                ],
                value=py_tree.Name("c", py_tree.Load()),
            )),
        ])

    def test_delete(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("del a", py_tree.Delete(targets=[
                py_tree.Name("a", py_tree.Del()),
            ])),
            ("del a, b", py_tree.Delete(targets=[
                py_tree.Name("a", py_tree.Del()),
                py_tree.Name("b", py_tree.Del()),
            ])),
            ("del (a, b)", py_tree.Delete(targets=[
                py_tree.Tuple([
                                 py_tree.Name("a", py_tree.Del()),
                                 py_tree.Name("b", py_tree.Del()),
                             ], py_tree.Del()),
            ])),
            ("del (a\n, b)", py_tree.Delete(targets=[
                py_tree.Tuple([
                                 py_tree.Name("a", py_tree.Del()),
                                 py_tree.Name("b", py_tree.Del())
                             ], py_tree.Del()),
            ])),
            ("del (a\n, b), c", py_tree.Delete(targets=[
                py_tree.Tuple([
                                 py_tree.Name("a", py_tree.Del()),
                                 py_tree.Name("b", py_tree.Del())
                             ], py_tree.Del()),
                py_tree.Name("c", py_tree.Del()),
            ])),
        ])

    def test_raise(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("raise", py_tree.Raise(
                None, None
            )),
            ("raise err", py_tree.Raise(
                py_tree.Name("err", py_tree.Load()),
                None
            )),
            ("raise err_1 from err_2", py_tree.Raise(
                py_tree.Name("err_1", py_tree.Load()),
                py_tree.Name("err_2", py_tree.Load()),
            )),
        ])

    def test_import_module(self):
        yield from self.yield_tests(self.check_code_translation, [
            (  # Single import
               "import apple",
               py_tree.Import([
                   py_tree.alias("apple", None),
               ])
            ),
            (  # Single subpackage import
               "import apple.ball",
               py_tree.Import([
                   py_tree.alias("apple.ball", None),
               ])
            ),
            (  # Single alias import
               "import apple as ball",
               py_tree.Import([
                   py_tree.alias("apple", "ball"),
               ])
            ),
            (  # Multiple imports, 1 alias, 1 simple
               "import apple as ball, cat",
               py_tree.Import([
                   py_tree.alias("apple", "ball"),
                   py_tree.alias("cat", None),
               ])
            ),
            (  # Multiple alias imports
               "import apple as ball, cat as dog",
               py_tree.Import([
                   py_tree.alias("apple", "ball"),
                   py_tree.alias("cat", "dog"),
               ])
            ),
            (  # Multiple alias imports from subpackage
               "import apple.ball as ball, cat as dog",
               py_tree.Import([
                   py_tree.alias("apple.ball", "ball"),
                   py_tree.alias("cat", "dog"),
               ])
            ),
        ])

    def test_from_module_import_star(self):
        yield from self.yield_tests(self.check_code_translation, [
            (
                "from apple import *",
                py_tree.ImportFrom(
                    "apple", [
                        py_tree.alias("*", None)
                    ],
                    0
                )
            ),
            (
                "from apple.ball import *",
                py_tree.ImportFrom(
                    "apple.ball", [
                        py_tree.alias("*", None)
                    ],
                    0
                )
            ),
        ])

    def test_from_module_import_names(self):
        yield from self.yield_tests(self.check_code_translation, [
            (
                "from apple import ball",
                py_tree.ImportFrom(
                    "apple", [
                        py_tree.alias("ball", None)
                    ],
                    0
                )
            ),
            (
                "from apple import ball as cat",
                py_tree.ImportFrom(
                    "apple", [
                        py_tree.alias("ball", "cat")
                    ],
                    0
                )
            ),
        ])

    def test_from_submodule_import_names(self):
        yield from self.yield_tests(self.check_code_translation, [
            (
                "from apple.ball import (\n    cat, \n    dog,)",
                py_tree.ImportFrom(
                    "apple.ball",
                    [
                        py_tree.alias("cat", None),
                        py_tree.alias("dog", None),
                    ],
                    0
                )
            ),
            (
                "from apple.ball import cat as dog",
                py_tree.ImportFrom(
                    "apple.ball",
                    [
                        py_tree.alias("cat", "dog")
                    ],
                    0
                )
            ),
            (
                "from apple.ball import cat as dog, egg",
                py_tree.ImportFrom(
                    "apple.ball",
                    [
                        py_tree.alias("cat", "dog"),
                        py_tree.alias("egg", None),
                    ],
                    0
                )
            ),
            (
                "from apple.ball import (\n    cat as dog, \n    egg as frog)",
                py_tree.ImportFrom(
                    "apple.ball",
                    [
                        py_tree.alias("cat", "dog"),
                        py_tree.alias("egg", "frog"),
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
                py_tree.If(
                    py_tree.NameConstant(True),
                    [py_tree.Pass()],
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
                py_tree.If(
                    py_tree.Name(
                        "first_cond", py_tree.Load()
                    ),
                    [py_tree.Expr(
                        py_tree.Name("first", py_tree.Load())
                    )],
                    [
                        py_tree.If(
                            py_tree.Name("second_cond", py_tree.Load()),
                            [py_tree.Expr(
                                py_tree.Name("second", py_tree.Load())
                            )],
                            [py_tree.Expr(
                                py_tree.Name("third", py_tree.Load())
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
                py_tree.Try(
                    [py_tree.Pass()],
                    [py_tree.ExceptHandler(
                        py_tree.Name("SomeException", py_tree.Load()),
                        "error",
                        [py_tree.Pass()]
                    )],
                    [py_tree.Pass()],
                    [py_tree.Pass()]
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
                py_tree.With(
                    [py_tree.withitem(
                        py_tree.Name("some_context", py_tree.Load()),
                        py_tree.Name("some_name", py_tree.Store()),
                    )],
                    [py_tree.Pass()]
                )
            )
        ])


class TestsCompoundStatementPart(CodeTest):
    """Tests for statements that can only be part of compound statements
    """

    def process_node(self, node):
        return node.body[0].body

    def test_while(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("while True:\n pass", py_tree.Pass()),
            ("while True:\n break", py_tree.Break()),
            ("while True:\n continue", py_tree.Continue()),
        ])

    def test_for(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("for val in iter:\n pass", py_tree.Pass()),
            ("for val in iter:\n break", py_tree.Break()),
            ("for val in iter:\n continue", py_tree.Continue()),
        ])

    def test_function_parts(self):
        yield from self.yield_tests(self.check_code_translation, [
            ("def foo():\n pass", py_tree.Pass()),
            ("def foo():\n global a", py_tree.Global(['a'])),
            ("def foo():\n global a, b", py_tree.Global(['a', "b"])),
            ("def foo():\n nonlocal a", py_tree.Nonlocal(['a'])),
            ("def foo():\n nonlocal a, b", py_tree.Nonlocal(['a', "b"])),
        ])


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
