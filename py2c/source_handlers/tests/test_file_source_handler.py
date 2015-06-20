"""Unit-tests for `py2c.source_handlers.FileSourceHandler
"""

import os
import inspect
import tempfile

from py2c.abc.source_handler import (
    SourceHandler, CouldNotGetSourceError, CouldNotWriteSourceError
)
from py2c.source_handlers import FileSourceHandler

from nose.tools import assert_raises, assert_equal
from py2c.tests import Test, data_driven_test


class TestFileSourceHandler(Test):
    """py2c.source_handlers.FileSourceHandler
    """
    _temporary_files = []

    def get_temporary_file_name(self):
        _, val = tempfile.mkstemp(text=True)
        self._temporary_files.append(val)
        return val

    def read_from_file(self, file_name):
        with open(file_name) as f:
            return f.read()

    def write_to_file(self, file_name, text):
        with open(file_name, "wt") as f:
            f.write(text)

    @classmethod
    def tearDownClass(cls):
        for file_name in list(cls._temporary_files):
            os.remove(file_name)

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------
    def test_is_a_SourceHandler(self):
        assert issubclass(FileSourceHandler, SourceHandler), (
            "Should be a SourceHandler subclass"
        )
        assert isinstance(FileSourceHandler(""), SourceHandler), (
            "Should be a SourceHandler instance"
        )

    def test_needs_an_argument_to_initialize(self):
        with assert_raises(TypeError) as context:
            FileSourceHandler()
        self.assert_error_message_contains(context.exception, ["require", "1"])

    @data_driven_test(described=True, prefix="checks file name before ", data=[  # noqa
        ("getting sources", CouldNotGetSourceError, "get_source"),
        ("writing sources", CouldNotWriteSourceError, "write_source", ""),
    ])
    def check_file_name_matches(self, error, method, *args):
        file_name = self.get_temporary_file_name()
        fsh = FileSourceHandler(file_name)

        with assert_raises(error) as context:
            getattr(fsh, method)(file_name[:-1] + ".non-existent", *args)

        self.assert_error_message_contains(
            context.exception, ["unexpected", "file name"]
        )

    def test_lists_only_passed_file_name(self):
        fsh = FileSourceHandler("magic.py")

        files = fsh.get_files()
        assert inspect.isgenerator(files), (
            "FileSourceHandler.get_files should return a generator"
        )

        assert_equal(list(files), ["magic.py"])

    def test_gets_correct_source_correctly(self):
        file_name = self.get_temporary_file_name()
        self.write_to_file(file_name, "Hello World!")

        fsh = FileSourceHandler(file_name)
        assert_equal(fsh.get_source(file_name), "Hello World!")

    def test_writes_source_correctly(self):
        file_name = self.get_temporary_file_name()

        fsh = FileSourceHandler(file_name)
        fsh.write_source(file_name, "Hello World!")

        assert_equal(self.read_from_file(file_name), "Hello World!")

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
