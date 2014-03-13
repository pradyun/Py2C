#!/usr/bin/python3
"""Tests for the Python -> AST translator
"""

#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------


import random
import unittest

import sys
# Mock
if sys.version_info[:2] < (3, 3):
    import mock
else:
    import unittest.mock as mock

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
        my_mock = mock.Mock()
        my_mock.lineno = num

        errors = self.template([("foo", my_mock)])

        err_msg = errors[0]
        self.assertIn("foo", err_msg)
        self.assertIn("line", err_msg.lower())
        self.assertIn(str(num), err_msg)


@unittest.skip("Translator not ready!")
class CodeTestCase(unittest.TestCase):
    """Base for Python code to AST translation
    """
    longMessage = True  # useful!

    def template(self, tests, remove_expr=False):
        failed = []
        for code, expected in tests:
            result = self.process_node(self.translator.get_node(code))

            if len(result) == 1:
                result = result[0]
            # Remove the code from Expr
            if remove_expr:
                result = result.value

            if expected != result:
                failed.append(code)
            print(expected)
            print(result)
            print()

        if failed:
            self.fail(
                "Incorrect values returned for {0}".format(
                    # Failed code in quotes
                    ", ".join(map(repr, failed)))
            )

    def setUp(self):
        self.translator = PythonTranslator()

    def process_node(self, node):
        return node.body


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
        print((s, dual_ast.Int(eval(s))) for s in tests)
        self.template([
            (s, dual_ast.Int(eval(s))) for s in tests
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
            (s, dual_ast.Float(eval(s))) for s in tests
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
            (s, dual_ast.Complex(eval(s))) for s in tests
        ], remove_expr=True)

    def test_str(self):
        tests = [
            '"abc"',
            '"abc"',
            "'''abc'''",
            '"""abc"""',
            r'r"a\bc"',
        ]
        self.template([
            (s, dual_ast.Str(eval(s))) for s in tests
        ], remove_expr=True)


class SimpleStmtTestCase(CodeTestCase):
    """Tests for simple statements
    """

    def test_assert(self):
        self.template([
            ("assert False", dual_ast.Assert(dual_ast.Name(False))),
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

    def test_del(self):
        self.template([
            ("del a", dual_ast.Delete(targets=[
                dual_ast.Name("a")
            ])),
            ("del a, b", dual_ast.Delete(targets=[
                dual_ast.Name("a"),
                dual_ast.Name("b"),
            ])),
            ("del (a, b)", dual_ast.Delete(targets=[dual_ast.Tuple([
                dual_ast.Name("a"),
                dual_ast.Name("b"),
            ])])),
            ("del (a\n, b)", dual_ast.Delete(targets=[dual_ast.Tuple([
                dual_ast.Name("a"),
                dual_ast.Name("b")
            ])])),
        ])

    def test_raise(self):
        self.template([
            ("raise", dual_ast.Raise(None, None, None, None)),
            ("raise err", dual_ast.Raise(
                dual_ast.Name("err"),
                None, None, None
            )),
            ("raise err_1 from err_2", dual_ast.Raise(
                dual_ast.Name("err_1"),
                None, None,
                dual_ast.Name("err_2"),
            )),
        ])

    def test_import_module(self):
        self.template([
            (  # Simple Import
                "import apple",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Name("apple"),
                        None
                    )
                ])
            ),
            (
                "import apple.ball",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Attribute(
                            dual_ast.Name("apple"), [
                                dual_ast.Name("ball")
                            ]  # noqa
                        ),
                        None
                    )
                ])
            ),
            (
                "import apple as ball",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Name("apple"),
                        dual_ast.Name("ball")
                    ),
                ])
            ),
            (
                "import apple as ball, cat",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Name("apple"),
                        dual_ast.Name("ball")
                    ),
                    dual_ast.Alias(
                        dual_ast.Name("cat"),
                        None
                    ),
                ])
            ),
            (
                "import apple as ball, cat as dog",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Name("apple"),
                        dual_ast.Name("ball")
                    ),
                    dual_ast.Alias(
                        dual_ast.Name("cat"),
                        dual_ast.Name("dog"),
                    ),
                ])
            ),
            (
                "import apple.ball as ball, cat as dog",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Attribute(
                            dual_ast.Name("apple"), [
                                dual_ast.Name("ball")
                            ]
                        ),
                        dual_ast.Name("ball")
                    ),
                    dual_ast.Alias(
                        dual_ast.Name("cat"),
                        dual_ast.Name("dog"),
                    ),
                ])
            ),
        ])

    def test_from_module_import_star(self):
        self.template([
            (
                "from apple import *",
                dual_ast.Import(
                    dual_ast.Name("apple"), []
                )
            ),
            (
                "from apple.ball import *",
                dual_ast.Import(
                    dual_ast.Attribute(
                        dual_ast.Name("apple"), [
                            dual_ast.Name("ball")
                        ]
                    ),
                    []
                )
            ),
        ])

    def test_from_module_import_names(self):
        self.template([
            (
                "from apple import ball",
                dual_ast.Import(
                    dual_ast.Name("apple"), [
                        dual_ast.Alias(
                            dual_ast.Name("ball"),
                            None
                        )
                    ]
                )
            ),
            (
                "from apple import ball as cat",
                dual_ast.Import(
                    dual_ast.Name("apple"), [
                        dual_ast.Alias(
                            dual_ast.Name("ball"),
                            dual_ast.Name("cat"),
                        )
                    ]
                )
            ),
            (
                "from apple.ball import cat as dog",
                dual_ast.Import(
                    dual_ast.Attribute(
                        dual_ast.Name("apple"), [
                            dual_ast.Name("ball")
                        ]
                    ),
                    [
                        dual_ast.Alias(
                            dual_ast.Name("cat"),
                            dual_ast.Name("dog"),
                        ),
                    ]
                )
            ),
            (
                "from apple.ball import cat as dog, egg",
                dual_ast.Import(
                    dual_ast.Attribute(
                        dual_ast.Name("apple"), [
                            dual_ast.Name("ball")
                        ]
                    ),
                    [
                        dual_ast.Alias(
                            dual_ast.Name("cat"),
                            dual_ast.Name("dog"),
                        ),
                        dual_ast.Alias(
                            dual_ast.Name("egg"),
                            None
                        ),
                    ]
                )
            ),
            (
                "from apple.ball import (\n    cat, \n    dog as egg)",
                dual_ast.Import(
                    dual_ast.Attribute(
                        dual_ast.Name("apple"), [
                            dual_ast.Name("ball")
                        ]
                    ),
                    [
                        dual_ast.Alias(
                            dual_ast.Name("cat"),
                            None
                        ),
                        dual_ast.Alias(
                            dual_ast.Name("dog"),
                            dual_ast.Name("egg")
                        ),
                    ]
                )
            ),
            (
                "from apple.ball import (\n    cat as dog, \n    egg as frog)",
                dual_ast.Import(
                    dual_ast.Attribute(
                        dual_ast.Name("apple"), [
                            dual_ast.Name("ball")
                        ]
                    ),
                    [
                        dual_ast.Alias(
                            dual_ast.Name("cat"),
                            dual_ast.Name("dog"),
                        ),
                        dual_ast.Alias(
                            dual_ast.Name("egg"),
                            dual_ast.Name("frog"),
                        ),
                    ]
                )
            ),
            (
                "from apple.ball import (\n    cat, \n    dog,)",
                dual_ast.Import(
                    dual_ast.Attribute(
                        dual_ast.Name("apple"), [
                            dual_ast.Name("ball")
                        ]
                    ),
                    [
                        dual_ast.Alias(
                            dual_ast.Name("cat"), None
                        ),
                        dual_ast.Alias(
                            dual_ast.Name("dog"), None
                        ),
                    ]
                )
            ),
        ])

    def test_future(self):
        self.template([
            (
                "from __future__ import with_statement",
                dual_ast.Future(
                    "with_statement",
                )
            ),
            (
                "import __future__ as future",
                dual_ast.Import(None, [
                    dual_ast.Alias(
                        dual_ast.Name("__future__"),
                        dual_ast.Name("future")
                    )
                ])
            ),
        ])


class LoopStmtTestCase(CodeTestCase):
    """Tests for statements that can only be inside loop statements
    """
    def process_node(self, node):
        # To be implemented
        pass

    def test_break(self):
        # To be implemented
        pass

    def test_continue(self):
        # To be implemented
        pass

    def test_pass(self):
        # To be implemented
        pass


class FunctionStmtTestCase(CodeTestCase):
    """Tests for statements that can only be inside functions
    """
    def process_node(self, node):
        # To be implemented
        pass

    def test_pass(self):
        # To be implemented
        pass

    def test_global(self):
        # To be implemented
        pass

    def test_nonlocal(self):
        # To be implemented
        pass

# TODO: More tests for the same.

if __name__ == '__main__':
    unittest.main()
