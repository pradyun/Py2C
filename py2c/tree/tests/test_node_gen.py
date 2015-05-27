"""Tests for the Generation of the AST nodes from the definitions.
"""

from textwrap import dedent

from py2c.tree.node_gen import (
    Parser, Definition, SourceGenerator, remove_comments, ParserError
)

from py2c.tests import Test
from nose.tools import assert_equal, assert_in, assert_raises


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
def check_remove_comments(test_string, expected):
    assert_equal(remove_comments(test_string), expected)


def test_remove_comments():
    """tree.node_gen.remove_comments\
    """  # Don't want a trailing newline in name
    yield from Test().yield_tests(check_remove_comments, [
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
            "full line comment with text on next line",
            "# test: [a,string]\nsome text!",
            "\nsome text!"
        ),
        (
            "an inline comment",
            "foo: [] # test: [a,string]",
            "foo: [] "
        ),
        (
            "an inline comment with a text on next line",
            "foo:[] # test\nsome text!",
            "foo:[] \nsome text!"
        )
    ], described=True, prefix="does remove correct sub-string given ")


class TestParser(Test):
    """tree.node_gen.Parser
    """
    parser = Parser()

    def check_property_parsing(self, test_string, expected):
        self.parser._reset()
        assert_equal(self.parser.parse(dedent(test_string)), tuple(expected))

    def test_parsing(self):
        """Tests Parser's parsing of properties
        """
        yield from self.yield_tests(self.check_property_parsing, [
            (
                "an node without parent and no fields",
                "foo",
                [Definition('foo', None, [])]
            ),
            (
                "an node with parent and no fields",
                "foo(Base)",
                [Definition('foo', 'Base', [])]
            ),
            (
                "an node without parent with zero fields",
                "foo: []",
                [Definition('foo', None, [])]
            ),
            (
                "an empty node with parent",
                "foo(AST): []",
                [Definition('foo', 'AST', [])]
            ),
            (
                "a node that inherits, with parent",
                "foo(AST): inherit",
                [Definition('foo', 'AST', 'inherit')]
            ),
            (
                "a simple node, without parent",
                "foo: [int bar]",
                [Definition(
                    'foo',
                    None,
                    [('bar', 'int', 'NEEDED')],
                )]
            ),
            (
                "a simple node, with parent",
                "foo(AST): [int bar]",
                [Definition(
                    'foo',
                    'AST',
                    [('bar', 'int', 'NEEDED')],
                )]
            ),
            (
                "a node with all modifiers",
                "FooBar: [int foo, int+ bar, int* baz, int? spam]",
                [
                    Definition(
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
                "multiple nodes with inheritance",
                """
                base1: [int field1]
                base2(base1): [int field2]
                obj(base2): []
                """,
                [
                    Definition(
                        "base1", None,
                        [("field1", "int", "NEEDED")]
                    ),
                    Definition(
                        "base2", "base1",
                        [("field2", "int", "NEEDED")]
                    ),
                    Definition(
                        "obj", "base2",
                        []
                    ),
                ]
            ),
            (
                "a node, without bothering about the indentation",
                """
                base1: [int field1]
                    base2(base1): [int field2]
                    obj(Definition): []
                """,
                [
                    Definition(
                        "base1", None,
                        [("field1", "int", "NEEDED")]
                    ),
                    Definition(
                        "base2", "base1",
                        [("field2", "int", "NEEDED")]
                    ),
                    Definition(
                        "obj", "Definition",
                        []
                    ),
                ]
            )
        ], described=True, prefix="does parse correctly ")

    def check_error_reporting(self, test_string, required_words):
        with assert_raises(ParserError) as context:
            Parser().parse(test_string)
        msg = context.exception.args[0].lower()

        for word in required_words:
            assert_in(word, msg)

    def test_error_reporting(self):
        """Tests Parser's error reports for important information
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
            ),
            (
                "a node that inherits, without parent",
                "foo: inherit",
                ['inherit', 'need', 'parent', 'foo']
            ),
        ], described=True, prefix="does report error given ")


class TestSourceGenerator(Test):
    """tree.node_gen.SourceGenerator
    """

    def check_generated_source(self, data, expected_output):
        src_gen = SourceGenerator()
        generated = src_gen.generate_sources(data)

        assert_equal(
            dedent(expected_output).strip(), generated.strip()
        )

    def test_code_generation(self):
        """Tests SourceGenerator's code-generation
        """
        yield from self.yield_tests(self.check_generated_source, [
            (
                "without fields, without parent",
                [Definition('FooBar', None, [])],
                """
                class FooBar(object):
                    @fields_decorator
                    def _fields(cls):
                        return []
                """
            ),
            (
                "without fields, with parent",
                [Definition('FooBar', 'AST', [])],
                """
                class FooBar(AST):
                    @fields_decorator
                    def _fields(cls):
                        return []
                """
            ),
            (
                "inheriting fields from parent",
                [Definition('FooBar', 'AST', 'inherit')],
                """
                class FooBar(AST):
                    @fields_decorator
                    def _fields(cls):
                        return AST._fields
                """
            ),
            (
                "with fields, without parent",
                [Definition(
                    'FooBar',
                    None,
                    [('bar', 'int', 'NEEDED')],
                )],
                """
                class FooBar(object):
                    @fields_decorator
                    def _fields(cls):
                        return [
                            ('bar', int, 'NEEDED'),
                        ]
                """
            ),
            (
                "with fields, with parent",
                [Definition(
                    'FooBar',
                    'AST',
                    [('bar', 'int', 'NEEDED')],
                )],
                """
                class FooBar(AST):
                    @fields_decorator
                    def _fields(cls):
                        return [
                            ('bar', int, 'NEEDED'),
                        ]
                """
            ),
            (
                "with fields, with parent, with all modifiers",
                [Definition(
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
                    @fields_decorator
                    def _fields(cls):
                        return [
                            ('foo', int, 'NEEDED'),
                            ('bar', int, 'ONE_OR_MORE'),
                            ('baz', int, 'ZERO_OR_MORE'),
                            ('spam', int, 'OPTIONAL'),
                        ]
                """
            ),
            (
                "with multiple fields",
                [
                    Definition(
                        'base1',
                        None,
                        [('field1', 'int', 'NEEDED')],
                    ),
                    Definition(
                        'base2',
                        'base1',
                        [('field2', 'int', 'NEEDED')],
                    ),
                    Definition(
                        'obj',
                        'base2',
                        [],
                    ),
                ],
                """
                class base1(object):
                    @fields_decorator
                    def _fields(cls):
                        return [
                            ('field1', int, 'NEEDED'),
                        ]


                class base2(base1):
                    @fields_decorator
                    def _fields(cls):
                        return [
                            ('field2', int, 'NEEDED'),
                        ]


                class obj(base2):
                    @fields_decorator
                    def _fields(cls):
                        return []
                """
            )
        ], described=True, prefix="does generate correct code for a node ")


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
