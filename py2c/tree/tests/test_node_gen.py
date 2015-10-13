"""Unit-tests for `py2c.tree.node_gen`
"""

from textwrap import dedent

from py2c.tree import node_gen

from py2c.tests import Test, data_driven_test
from nose.tools import assert_equal, assert_raises


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
@data_driven_test("node_gen-remove_comments.yaml")
def test_remove_comments(in_text, out_text):
    "py2c.tree.node_gen.remove_comments"
    assert_equal(node_gen.remove_comments(in_text), out_text)


class TestParser(Test):
    """py2c.tree.node_gen.Parser
    """

    @data_driven_test("node_gen-valid_cases.yaml")
    def test_valid_cases(self, in_text, node, **kwargs):
        node = self.load(node, {"Definition": node_gen.Definition})

        parser = node_gen.Parser()

        assert_equal(
            parser.parse(dedent(in_text)),
            tuple(node)
        )

    @data_driven_test("node_gen-invalid_cases.yaml")
    def test_invalid_cases(self, in_text, phrases):
        with assert_raises(node_gen.ParserError) as context:
            node_gen.Parser().parse(in_text)

        self.assert_error_message_contains(context.exception, phrases)


class TestSourceGenerator(Test):
    """py2c.tree.node_gen.SourceGenerator
    """

    @data_driven_test("node_gen-valid_cases.yaml")
    def test_valid_cases(self, out_text, node, **kwargs):
        node = self.load(node, {"Definition": node_gen.Definition})

        src_gen = node_gen.SourceGenerator()
        generated = src_gen.generate_sources(node)

        assert_equal(out_text.strip(), generated.strip())

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
