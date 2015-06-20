"""Unit-tests for `py2c.tree.node_gen`
"""

from textwrap import dedent

from py2c.tree import node_gen

from py2c.tests import Test, data_driven_test    # noqa
from nose.tools import assert_equal, assert_raises

import py2c.tree.tests.data_node_gen as data


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
@data_driven_test(data.remove_comments_cases, True, "removes comments correctly: ")  # noqa
def test_remove_comments(test_string, expected):
    "py2c.tree.node_gen.remove_comments"
    assert_equal(node_gen.remove_comments(test_string), expected)


class TestParser(Test):
    """py2c.tree.node_gen.Parser
    """

    @data_driven_test(data.Parser_valid_cases, True, "parses valid input correctly: ")  # noqa
    def test_valid_cases(self, test_string, expected, _):
        parser = node_gen.Parser()

        assert_equal(
            parser.parse(dedent(test_string)),
            tuple(expected)
        )

    @data_driven_test(data.Parser_invalid_cases, True, "raises error parsing: ")  # noqa
    def test_invalid_cases(self, test_string, required_phrases):
        with assert_raises(node_gen.ParserError) as context:
            node_gen.Parser().parse(test_string)

        self.assert_error_message_contains(context.exception, required_phrases)


class TestSourceGenerator(Test):
    """py2c.tree.node_gen.SourceGenerator
    """

    @data_driven_test(data.SourceGenerator_valid_cases, True, "generates code correctly: ")  # noqa
    def test_valid_cases(self, _, definitions, expected):
        src_gen = node_gen.SourceGenerator()
        generated = src_gen.generate_sources(definitions)

        assert_equal(dedent(expected).strip(), generated.strip())

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
