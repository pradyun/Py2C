"""Unit-tests for `py2c.abc.source_handler.SourceHandler`
"""

from py2c.tests import Test, data_driven_test
from nose.tools import assert_raises

from py2c.abc.source_handler import SourceHandler


# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------
class GoodSourceHandler(SourceHandler):

    def get_files(self):
        return ["a"]

    def get_source(self, file_name):
        return "source_code"

    def write_source(self, file_name, source):
        pass


class EmptySourceHandler(SourceHandler):
    pass


class NoGetSourceSourceHandler(SourceHandler):

    def get_files(self):
        return ["a"]

    def write_source(self, file_name, source):
        pass


class NoWriteSourceSourceHandler(SourceHandler):

    def get_files(self):
        return ["a"]

    def get_source(self, file_name):
        return "source_code"


class NoGetFilesSourceHandler(SourceHandler):

    def get_source(self, file_name):
        return "source_code"

    def write_source(self, file_name, source):
        pass


class SuperCallingSourceHandler(SourceHandler):

    def get_files(self):
        super().get_files()

    def get_source(self, file_name):
        super().get_source(file_name)

    def write_source(self, file_name, source):
        super().write_source(file_name, source)

initialization_invalid_cases = [
    {
        "description": "without any method",
        "args": [
            EmptySourceHandler, TypeError, ["EmptySourceHandler"]
        ]
    },
    {
        "description": "without get_files method",
        "args": [
            NoGetFilesSourceHandler, TypeError,
            ["NoGetFilesSourceHandler", "get_files"]
        ]
    },
    {
        "description": "without get_source method",
        "args": [
            NoGetSourceSourceHandler, TypeError,
            ["NoGetSourceSourceHandler", "get_source"]
        ]
    },
    {
        "description": "without write_source method",
        "args": [
            NoWriteSourceSourceHandler, TypeError,
            ["NoWriteSourceSourceHandler", "write_source"]
        ]
    },
    # MARK:: Should I add the only-one method cases as well?
]


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestBaseSourceHandler(Test):
    """py2c.abc.source_handler.SourceHandler
    """

    def test_initializes_a_subclass_with_all_required_methods(self):
        GoodSourceHandler()

    @data_driven_test(initialization_invalid_cases, prefix="raises error initializing subclass: ")  # noqa
    def test_initialization_invalid_cases(self, source_handler_class, err, required_phrases):  # noqa
        with assert_raises(err) as context:
            source_handler_class()

        self.assert_error_message_contains(context.exception, required_phrases)

    def test_raises_error_when_subclass_calls_an_abstract_method(self):
        source_handler = SuperCallingSourceHandler()

        with assert_raises(NotImplementedError):
            source_handler.get_files()

        with assert_raises(NotImplementedError):
            source_handler.get_source("")

        with assert_raises(NotImplementedError):
            source_handler.write_source("", "")

    def test_recognizes_subclass(self):
        assert issubclass(GoodSourceHandler, SourceHandler), (
            "Did not recognize subclass"
        )


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
