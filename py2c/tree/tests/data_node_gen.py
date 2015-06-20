"""Data for unit-tests for `py2c.tree.node_gen`
"""

from py2c.tree import node_gen

# =============================================================================
# Test cases
# =============================================================================

remove_comments_cases = [
    (
        "an empty string",
        "",
        ""
    ),
    (
        "a string with full line comment without trailing newline",
        "#test: [a,string]",
        ""
    ),
    (
        "a string with full line comment with a trailing newline",
        "# test: [a,string]\n",
        "\n"
    ),
    (
        "a string with full line comment with a trailing newline and text on next line",  # noqa
        "# test: [a,string]\nbar: []",
        "\nbar: []"
    ),
    (
        "a string with inline comment with a trailing newline",
        "foo: [] # test: [a,string]",
        "foo: [] "
    ),
    (
        "a string with inline comment with a trailing newline and text on next line",  # noqa
        "foo: [] # test: [a,string]\nbar: []",
        "foo: [] \nbar: []"
    ),
]

# -----------------------------------------------------------------------------

Parser_valid_cases = [
    (
        "single node with no parent and zero fields",
        "FooBar",
        [node_gen.Definition('FooBar', None, [])],
        """
        class FooBar(object):
            @fields_decorator
            def _fields(cls):
                return []
        """
    ),
    (
        "single node with parent and zero fields",
        "FooBar(Base)",
        [node_gen.Definition('FooBar', 'Base', [])],
        """
        class FooBar(Base):
            @fields_decorator
            def _fields(cls):
                return []
        """
    ),
    (
        "single node with no parent and zero fields",
        "FooBar: []",
        [node_gen.Definition('FooBar', None, [])],
        """
        class FooBar(object):
            @fields_decorator
            def _fields(cls):
                return []
        """
    ),
    (
        "single node with parent and inherited fields",
        "FooBar(AST): inherit",
        [node_gen.Definition('FooBar', 'AST', 'inherit')],
        """
        class FooBar(AST):
            pass
        """
    ),
    (
        "single node with no parent and one field",
        "FooBar: [int bar]",
        [node_gen.Definition('FooBar', None, [('bar', 'int', 'NEEDED')])],
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
        "single node with parent and one field",
        "FooBar(AST): [int bar]",
        [node_gen.Definition('FooBar', 'AST', [('bar', 'int', 'NEEDED')])],
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
        "single node with no parent and 4 fields of all types",
        "FooBar: [int f1, int+ f2, int* f3, int? f4]",
        [
            node_gen.Definition(
                "FooBar", None,
                [
                    ('f1', 'int', 'NEEDED'),
                    ('f2', 'int', 'ONE_OR_MORE'),
                    ('f3', 'int', 'ZERO_OR_MORE'),
                    ('f4', 'int', 'OPTIONAL'),
                ]
            )
        ],
        """
        class FooBar(object):
            @fields_decorator
            def _fields(cls):
                return [
                    ('f1', int, 'NEEDED'),
                    ('f2', int, 'ONE_OR_MORE'),
                    ('f3', int, 'ZERO_OR_MORE'),
                    ('f4', int, 'OPTIONAL'),
                ]
        """
    ),
    (
        "multiple nodes with inheritance",
        """
        base1: [int field1]
        base2(base1): [int field2]
        obj(base2): []
        """,
        [
            node_gen.Definition("base1", None, [("field1", "int", "NEEDED")]),
            node_gen.Definition("base2", "base1", [("field2", "int", "NEEDED")]),  # noqa
            node_gen.Definition("obj", "base2", []),
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
    ),
    (
        "multiple nodes without bothering about the indentation",
        """
        base1: [int field1]
            base2(base1): [int field2]
            obj: []
        """,
        [
            node_gen.Definition("base1", None, [("field1", "int", "NEEDED")]),
            node_gen.Definition("base2", "base1", [("field2", "int", "NEEDED")]),  # noqa
            node_gen.Definition("obj", None, []),
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


        class obj(object):
            @fields_decorator
            def _fields(cls):
                return []
        """
    )
]

Parser_invalid_cases = [
    (
        "multiple attributes with same name",
        "foo: [int bar, str bar]",  # type should not matter
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
        ["not", "generate", "token", "$foo"]
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
]

SourceGenerator_valid_cases = Parser_valid_cases
