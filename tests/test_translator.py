#!/usr/bin/env python
import sys
import random
import unittest

import support

from py2c import dual_ast
from py2c.translator import PythonTranslator, TranslationError


needs_python_2 = unittest.skipUnless(sys.version_info[0] < 3, "Need Python 2")
needs_python_3 = unittest.skipUnless(sys.version_info[0] > 2, "Need Python 3")


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

    @needs_python_2
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

    @needs_python_2
    def test_raise_python_2(self):
        self.template([
            ("raise", dual_ast.Raise(None, None, None, None)),
            ("raise err", dual_ast.Raise(
                dual_ast.Name("err"),
                None, None, None
            )),
            ("raise err_type, None, err_tb", dual_ast.Raise(
                dual_ast.Name("err_type"),
                # If first object is an instance, second object has to be 'None'
                dual_ast.Name("None"),
                dual_ast.Name("err_tb"),
                None
            )),
            ("raise err_type, err_val, err_tb", dual_ast.Raise(
                dual_ast.Name("err_type"),
                dual_ast.Name("err_val"),
                dual_ast.Name("err_tb"),
                None
            )),
        ])

    @needs_python_3
    def test_raise_python_3(self):
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

    @needs_python_2
    def test_exec(self):
        self.template([
            (
                "exec 'x = 1'",
                dual_ast.Exec(
                    dual_ast.Str('x = 1'),
                    None,
                    None
                )
            ),
            (
                "exec 'x = 1' in global_dict",
                dual_ast.Exec(
                    dual_ast.Str('x = 1'),
                    dual_ast.Name('global_dict'),
                    None
                )
            ),
            (
                "exec 'x = 1' in global_dict, local_dict",
                dual_ast.Exec(
                    dual_ast.Str('x = 1'),
                    dual_ast.Name('global_dict'),
                    dual_ast.Name('local_dict')
                )
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

    @needs_python_3
    def test_nonlocal(self):
        # To be implemented
        pass

# TODO: More tests for the same.

if __name__ == '__main__':
    unittest.main()
