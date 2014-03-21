#!/usr/bin/python3
"""Tests for the generation of the AST nodes from the definitions.
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
import sys
import unittest
from textwrap import dedent

sys.path.append(__file__ + "/../..")
import ast_gen
sys.path.pop()
# It is refered multiple times
Node = ast_gen.Node


class ParserTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for Parsing of the AST file declarations.

    NOTE: We convert the lists into tuples
    """
    def setUp(self):
        self.parser = ast_gen.Parser()

    def template(self, test_string, expected):
        result = self.parser.parse(dedent(test_string))
        self.assertEqual(result, tuple(expected))


class CommentTestCase(ParserTestCase):
    """Tests for Parser's comment handling capability
    """

    def template(self, test_string, expected):
        self.assertEqual(
            ast_gen.remove_comments(test_string),
            expected
        )

    def test_comment_only_line(self):
        "Checks if Parser handles empty lines with comments correctly"
        self.template(
            "#test: [a,string]",
            ""
        )

    def test_comment_empty_line(self):
        "Checks if Parser handles empty lines with comments correctly"
        self.template(
            "",
            ""
        )

    def test_comment_no_arg(self):
        "Checks if Parser handles Nodes with comments correctly"
        self.template(
            "foo: [] #test: [a,string]",
            "foo: [] "
        )

    def test_comment_newline(self):
        "Checks if Parser handles multiple lines with comments correctly"
        self.template(
            "foo:[] # test\nblah: []",
            "foo:[] \nblah: []"
        )


class PropertyTestCase(ParserTestCase):
    """Tests for Parser's parsing of the Definitions
    """

    def test_no_attr_no_parent(self):
        self.template(
            "foo: []",
            [Node('foo', None, [])]
        )

    def test_no_attr_parent(self):
        self.template(
            "foo(AST): []",
            [Node('foo', 'AST', [])]
        )

    def test_attr_no_parent(self):
        self.template(
            "foo: [int bar]",
            [Node(
                'foo',
                None,
                [('bar', 'int', 'NEEDED')],
            )]
        )

    def test_attr_parent(self):
        self.template(
            "foo(AST): [int bar]",
            [Node(
                'foo',
                'AST',
                [('bar', 'int', 'NEEDED')],
            )]
        )

    def test_modifiers(self):
        self.template(
            "FooBar: [int foo, int+ bar, int* baz, int? spam]",
            [
                Node(
                    "FooBar",
                    None,
                    [
                        ('foo', 'int', 'NEEDED'),
                        ('bar', 'int', 'ONE_OR_MORE'),
                        ('baz', 'int', 'ZERO_OR_MORE'),
                        ('spam', 'int', 'OPTIONAL'),
                    ]
                )
            ]
        )

    def test_multiple(self):
        self.template(
            """
            base1: [int field1]
            base2(base1): [int field2]
            obj(base2): []
            """,
            [
                Node(
                    "base1", None,
                    [("field1", "int", "NEEDED")]
                ),
                Node(
                    "base2", "base1",
                    [("field2", "int", "NEEDED")]
                ),
                Node(
                    "obj", "base2",
                    []
                ),
            ]
        )


class ErrorsTestCase(ParserTestCase):
    """Tests for errors generated by Parser
    """
    def test_duplicated_attr(self):
        text = "foo: [int bar, int bar]"

        with self.assertRaises(ast_gen.ParserError) as context:
            self.parser.parse(text)
        msg = context.exception.args[0].lower()

        self.assertIn("multiple", msg)
        self.assertIn("attribute", msg)
        self.assertIn("foo", msg)
        self.assertIn("bar", msg)

    def test_duplicated_declartion(self):
        s = "foo: [int bar, int bar]"
        text = s + "\n" + s

        with self.assertRaises(ast_gen.ParserError) as context:
            self.parser.parse(text)

        msg = context.exception.args[0].lower()
        self.assertIn("multiple", msg)
        self.assertIn("declaration", msg)
        self.assertIn("foo", msg)

    def test_invalid_token(self):
        text = "$foo: []"

        with self.assertRaises(ast_gen.ParserError) as context:
            self.parser.parse(text)
        msg = context.exception.args[0].lower()

        self.assertIn("token", msg)
        self.assertIn("unable", msg)
        self.assertIn("$foo", msg)

    def test_invalid_definition(self):
        text = "foo: [bar, baz]"

        with self.assertRaises(ast_gen.ParserError) as context:
            self.parser.parse(text)
        msg = context.exception.args[0].lower()

        self.assertIn("unexpected", msg)
        self.assertIn("','", msg)


class SourceGeneratorTestCase(unittest.TestCase):
    """Tests for the code generation
    """
    def template(self, data, expected_output):
        self.src_gen = ast_gen.SourceGenerator()
        generated = self.src_gen.generate_sources(data)

        self.assertEqual(
            dedent(expected_output).strip(), generated.strip()
        )

    def test_no_attr_no_parent(self):
        self.template(
            [Node('FooBar', None, [])],
            """
            class FooBar(object):
                _fields = []
            """
        )

    def test_no_attr_parent(self):
        self.template(
            [Node('FooBar', 'AST', [])],
            """
            class FooBar(AST):
                _fields = AST._fields
            """
        )

    def test_attr_no_parent(self):
        self.template(
            [Node(
                'FooBar',
                None,
                [('bar', 'int', 'NEEDED')],
            )],
            """
            class FooBar(object):
                _fields = [
                    ('bar', int, NEEDED),
                ]
            """
        )

    def test_attr_parent(self):
        self.template(
            [Node(
                'FooBar',
                'AST',
                [('bar', 'int', 'NEEDED')],
            )],
            """
            class FooBar(AST):
                _fields = AST._fields + [
                    ('bar', int, NEEDED),
                ]
            """
        )

    def test_modifiers(self):
        self.template(
            [Node(
                'FooBar',
                'AST',
                [
                    ('foo', 'int', 'NEEDED'),
                    ('bar', 'int', 'ONE_OR_MORE'),
                    ('baz', 'int', 'ZERO_OR_MORE'),
                    ('spam', 'int', 'OPTIONAL'),
                ]
            )],
            """
            class FooBar(AST):
                _fields = AST._fields + [
                    ('foo', int, NEEDED),
                    ('bar', int, ONE_OR_MORE),
                    ('baz', int, ZERO_OR_MORE),
                    ('spam', int, OPTIONAL),
                ]
            """
        )

    def test_multiple(self):
        self.template(
            [
                Node(
                    'base1',
                    None,
                    [('field1', 'int', 'NEEDED')],
                ),
                Node(
                    'base2',
                    'base1',
                    [('field2', 'int', 'NEEDED')],
                ),
                Node(
                    'obj',
                    'base2',
                    [],
                ),
            ],
            """
            class base1(object):
                _fields = [
                    ('field1', int, NEEDED),
                ]


            class base2(base1):
                _fields = base1._fields + [
                    ('field2', int, NEEDED),
                ]


            class obj(base2):
                _fields = base2._fields
            """
        )


if __name__ == '__main__':
    unittest.main()
