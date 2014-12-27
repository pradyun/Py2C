"""Tests for the Generation of the AST nodes from the definitions.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from textwrap import dedent

from py2c.tests import Test
from nose.tools import assert_equal, assert_in, assert_raises


def get_ast_gen():
    # Imports ast_gen.py for testing purposes.
    import sys
    from os.path import dirname, exists, join

    path = dirname(dirname(dirname(__file__)))

    # This if statement exists to prevent the user from getting a wierd
    # import error about some non-existent file. Instead
    if exists(join(path, "ast_gen.py")):
        sys.path.append(path)
        import ast_gen
        sys.path.pop()
    else:
        raise ImportError(
            "Can't import ast_gen.py. Please check that it exists."
        )

    return ast_gen

ast_gen = get_ast_gen()
del get_ast_gen


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestParser(Test):
    """ast_gen.Parser
    """

    #--------------------------------------------------------------------------
    # Comments
    #--------------------------------------------------------------------------
    def check_removal_of_comments(self, test_string, expected):
        assert_equal(
            ast_gen.remove_comments(test_string),
            expected
        )

    def test_comment_handling(self):
        """Tests ast_gen.Parser's comment handling capability
        """
        yield from self.yield_tests(self.check_removal_of_comments, [
            (
                "empty input",
                "",
                ""
            ),
            (
                "full line comment without trailing newline",
                "#test: [a,string]",
                ""
            ),
            (
                "full line comment with trailing newline",
                "#test: [a,string]\n",
                "\n"
            ),
            (
                "inline comment",
                "foo: [] #test: [a,string]",
                "foo: [] "
            ),
            (
                "inline comment with a rule on next line",
                "foo:[] # test\nblah: []",
                "foo:[] \nblah: []"
            )
        ], described=True, prefix="comment removal with ")

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    def check_property_parsing(self, test_string, expected):
        parser = ast_gen.Parser()
        assert_equal(parser.parse(dedent(test_string)), tuple(expected))

    def test_parsing(self):
        """Tests ast_gen.Parser's parsing of properties
        """
        yield from self.yield_tests(self.check_property_parsing, [
            (
                "an empty node, without parent",
                "foo: []",
                [ast_gen.Node('foo', None, [])]
            ),
            (
                "an empty node, with parent",
                "foo(AST): []",
                [ast_gen.Node('foo', 'AST', [])]
            ),
            (
                "a simple node, without parent",
                "foo: [int bar]",
                [ast_gen.Node(
                    'foo',
                    None,
                    [('bar', 'int', 'NEEDED')],
                )]
            ),
            (
                "a simple node, with parent",
                "foo(AST): [int bar]",
                [ast_gen.Node(
                    'foo',
                    'AST',
                    [('bar', 'int', 'NEEDED')],
                )]
            ),
            (
                "a node with all modifiers",
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
                "a node with multiple rules",
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
        ], described=True, prefix="parsing of ")

    #--------------------------------------------------------------------------
    # Errors
    #--------------------------------------------------------------------------
    def check_error_reporting(self, test_string, required_words):
        with assert_raises(ast_gen.ParserError) as context:
            ast_gen.Parser().parse(test_string)
        msg = context.exception.args[0].lower()

        for word in required_words:
            assert_in(word, msg)

    def test_error_reporting(self):
        """Tests ast_gen.Parser's error reports for important information
        """
        yield from self.yield_tests(self.check_error_reporting, [
            (
                "multiple attributes with same name",
                "foo: [int bar, int bar]",
                ["multiple", "attribute", "foo", "bar"]
            ),
            (
                "multiple declarations of node",
                "foo: []\n" * 2,
                ["multiple", "declaration", "foo"]
            ),
            (
                "invalid token",
                "$foo: []",
                ["token", "unable", "$foo"]
            ),
            (
                "no data-type",
                "foo: [bar, baz]",
                ["unexpected", "','"]
            )
        ], described=True, prefix="error reporting for ")


class TestSourceGenerator(Test):
    """ast_gen.SourceGenerator
    """

    def check_generated_source(self, data, expected_output):
        src_gen = ast_gen.SourceGenerator()
        generated = src_gen.generate_sources(data)

        assert_equal(
            dedent(expected_output).strip(), generated.strip()
        )

    def test_code_generation(self):
        """Tests ast_gen.SourceGenerator's code-generation
        """
        yield from self.yield_tests(self.check_generated_source, [
            (
                "without fields, without parent",
                [ast_gen.Node('FooBar', None, [])],
                """
                class FooBar(object):
                    _fields = []
                """
            ),
            (
                "without fields, with parent",
                [ast_gen.Node('FooBar', 'AST', [])],
                """
                class FooBar(AST):
                    _fields = []
                """
            ),
            (
                "with fields, without parent",
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
                "with fields, with parent",
                [ast_gen.Node(
                    'FooBar',
                    'AST',
                    [('bar', 'int', 'NEEDED')],
                )],
                """
                class FooBar(AST):
                    _fields = [
                        ('bar', int, NEEDED),
                    ]
                """
            ),
            (
                "with fields, with parent, with all modifiers",
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
                    _fields = [
                        ('foo', int, NEEDED),
                        ('bar', int, ONE_OR_MORE),
                        ('baz', int, ZERO_OR_MORE),
                        ('spam', int, OPTIONAL),
                    ]
                """
            ),
            (
                "with multiple fields",
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
                    _fields = [
                        ('field2', int, NEEDED),
                    ]


                class obj(base2):
                    _fields = []
                """
            )
        ], described=True, prefix="code generation for node ")

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
