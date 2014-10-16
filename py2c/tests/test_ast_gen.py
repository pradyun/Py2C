#!/usr/bin/python3
"""Tests for the Generation of the AST nodes from the definitions.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from textwrap import dedent

from py2c.tests import Test
from nose.tools import eq_, assert_in, assert_raises


def get_ast_gen():
    # Imports ast_gen.py for testing purposes.
    import os
    import sys

    path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # This if statement exists to prevent the user from getting a wierd
    # import error about some non-existent file. Instead
    if os.path.exists(os.path.join(path, "ast_gen.py")):
        sys.path.append(path)
        import ast_gen
        sys.path.pop()
    else:
        raise ImportError(
            "Can't import ast_gen.py, these tests can only be run on source "
            "package, not distribution."
        )

    return ast_gen

ast_gen = get_ast_gen()
del get_ast_gen

#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestParser(Test):
    """Tests for ast_gen.Parser
    """

    #--------------------------------------------------------------------------
    # Comments
    #--------------------------------------------------------------------------
    def check_remove_comment(self, test_string, expected):
        eq_(
            ast_gen.remove_comments(test_string),
            expected
        )

    def test_comment_handling(self):
        """Tests ast_gen.Parser's comment handling capability
        """
        yield from self.yield_tests(self.check_remove_comment, [
            (
                "#test: [a,string]",
                ""
            ),
            (
                "",
                ""
            ),
            (
                "foo: [] #test: [a,string]",
                "foo: [] "
            ),
            (
                "foo:[] # test\nblah: []",
                "foo:[] \nblah: []"
            )
        ])

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    def check_property_parsing(self, test_string, expected):
        parser = ast_gen.Parser()
        eq_(parser.parse(dedent(test_string)), tuple(expected))

    def test_parsing(self):
        """Tests ast_gen.Parser's parsing of properties
        """
        yield from self.yield_tests(self.check_property_parsing, [
            (
                "foo: []",
                [ast_gen.Node('foo', None, [])]
            ),
            (
                "foo(AST): []",
                [ast_gen.Node('foo', 'AST', [])]
            ),
            (
                "foo: [int bar]",
                [ast_gen.Node(
                    'foo',
                    None,
                    [('bar', 'int', 'NEEDED')],
                )]
            ),
            (
                "foo(AST): [int bar]",
                [ast_gen.Node(
                    'foo',
                    'AST',
                    [('bar', 'int', 'NEEDED')],
                )]
            ),
            (
                "FooBar: [int foo, int+ bar, int* baz, int? spam]",
                [
                    ast_gen.Node(
                        "FooBar", None,
                        [
                            ('foo', 'int', 'NEEDED'),
                            ('bar', 'int', 'ONE_OR_MORE'),
                            ('baz', 'int', 'ZERO_OR_MORE'),
                            ('spam', 'int', 'OPTIONAL'),
                        ]
                    )
                ]
            ),
            (
                """
                base1: [int field1]
                base2(base1): [int field2]
                obj(base2): []
                """,
                [
                    ast_gen.Node(
                        "base1", None,
                        [("field1", "int", "NEEDED")]
                    ),
                    ast_gen.Node(
                        "base2", "base1",
                        [("field2", "int", "NEEDED")]
                    ),
                    ast_gen.Node(
                        "obj", "base2",
                        []
                    ),
                ]
            )
        ])

    #--------------------------------------------------------------------------
    # Errors
    #--------------------------------------------------------------------------
    def check_error_report(self, test_string, required_words):
        with assert_raises(ast_gen.ParserError) as context:
            ast_gen.Parser().parse(test_string)
        msg = context.exception.args[0].lower()

        for word in required_words:
            assert_in(word, msg)

    def test_error_reporting(self):
        """Tests ast_gen.Parser's error reports for important information
        """
        yield from self.yield_tests(self.check_error_report, [
            ("foo: [int bar, int bar]", ["multiple", "attribute", "foo", "bar"]),  # noqa
            ("foo: [int bar, int bar]\n"*2, ["multiple", "declaration", "foo"]),  # noqa
            ("$foo: []", ["token", "unable", "$foo"]),
            ("foo: [bar, baz]", ["unexpected", "','"])
        ])


class TestSourceGenerator(Test):
    """Tests for ast_gen.SourceGenerator
    """

    def check_generated_source(self, data, expected_output):
        src_gen = ast_gen.SourceGenerator()
        generated = src_gen.generate_sources(data)

        eq_(
            dedent(expected_output).strip(), generated.strip()
        )

    def test_code_generation(self):
        """Tests ast_gen.SourceGenerator's code-generation
        """
        yield from self.yield_tests(self.check_generated_source, [
            (
                [ast_gen.Node('FooBar', None, [])],
                """
                class FooBar(object):
                    _fields = []
                """
            ),
            (
                [ast_gen.Node('FooBar', 'AST', [])],
                """
                class FooBar(AST):
                    _fields = AST._fields
                """
            ),
            (
                [ast_gen.Node(
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
            ),
            (
                [ast_gen.Node(
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
            ),
            (
                [ast_gen.Node(
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
            ),
            (
                [
                    ast_gen.Node(
                        'base1',
                        None,
                        [('field1', 'int', 'NEEDED')],
                    ),
                    ast_gen.Node(
                        'base2',
                        'base1',
                        [('field2', 'int', 'NEEDED')],
                    ),
                    ast_gen.Node(
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
        ])

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
