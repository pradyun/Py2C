"""Concrete implementations of SourceHandler
"""

import os
from os.path import join, relpath

from py2c.abc.source_handler import (
    SourceHandler, CouldNotGetSourceError, CouldNotWriteSourceError
)

__all__ = ["FileSourceHandler", "DirectorySourceHandler"]


# -----------------------------------------------------------------------------
# A grouping of common functionality (implementation detail)
# -----------------------------------------------------------------------------
# TEST:: Figure out how to test for failed read-write operations
class _FileSystemSourceHandler(SourceHandler):
    """An ABC for file-system related SourceHandlers

    Groups read-write handling common to file-system related SourceHandlers
    """

    def _get_source(self, file_name):
        """Read and return the contents of file_name.

        Raises CouldNotGetSourceError is reading fails.
        """
        try:
            with open(file_name) as f:
                return f.read()
        except OSError as err:  # coverage: not missing
            raise CouldNotGetSourceError(
                "Could not read from file '{}'".format(file_name)
            ) from err

    def _write_source(self, file_name, source):
        """Writes source to file_name.

        Raises CouldNotWriteSourceError is writing fails.
        """
        try:
            with open(file_name, "w") as f:
                f.write(source)
        except OSError as err:  # coverage: not missing
            raise CouldNotWriteSourceError(
                "Could not write to file '{}'".format(file_name)
            ) from err


# -----------------------------------------------------------------------------
# Concrete implementations
# -----------------------------------------------------------------------------
class FileSourceHandler(_FileSystemSourceHandler):
    """Source Handler for an OS file-system file
    """

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name

    def _ensure_same_file(self, file_name, error_cls):
        if file_name != self._file_name:
            raise error_cls(
                "Got unexpected file name: '{}'".format(file_name)
            )

    def get_source(self, file_name):
        self._ensure_same_file(file_name, CouldNotGetSourceError)
        return self._get_source(file_name)

    def write_source(self, file_name, source):
        self._ensure_same_file(file_name, CouldNotWriteSourceError)
        self._write_source(file_name, source)

    def get_files(self):
        yield self._file_name


# TEST:: Write tests once I know how this is supposed to work.
# NOTE:: Should we be file-type/file extension?
class DirectorySourceHandler(_FileSystemSourceHandler):  # coverage: not missing # noqa
    """Source Handler for an OS file-system directory
    """

    def __init__(self, base_dir):
        super().__init__()
        self._base_dir = base_dir

    def get_source(self, file_name):
        return self._get_source(join(self._base_dir, file_name))

    def write_source(self, file_name):
        self._write_source(join(self._base_dir, file_name))

    def get_files(self):
        file_set = set()

        for dir_, _, files in os.walk(self._base_dir):
            for file_name in files:
                rel_dir = relpath(dir_, self._base_dir)
                rel_file = join(rel_dir, file_name)
                file_set.add(rel_file)

        yield from file_set
