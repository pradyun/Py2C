"""An Abstract Base Class for SourceHandlers
"""

import abc

__all__ = [
    "SourceHandler",
    "SourceHandlerError", "CouldNotGetSourceError", "CouldNotWriteSourceError"
]


# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class SourceHandlerError(Exception):
    """Base class of all errors; should not be raised directly.
    """


class CouldNotGetSourceError(SourceHandlerError):
    """Raised when a SourceHandler fails to get source for file_name
    """


class CouldNotWriteSourceError(SourceHandlerError):
    """Raised when a SourceHandler fails to write source to file_name
    """


# -----------------------------------------------------------------------------
# Abstract Base SourceHandler
# -----------------------------------------------------------------------------
class SourceHandler(metaclass=abc.ABCMeta):
    """An ABC for SourceHandlers

    The abstraction of SourceHandler allows for a swap-in replacements to
    control what (and how) sources are provided for translation.
    """

    @abc.abstractmethod
    def get_source(self, file_name):
        """ABSTRACT: Get source code of `file_name`

        If source cannot be retrieved for some reason, subclasses should raise
        :class:`CouldNotGetSourceError`.

        Default implementation raises NotImplementedError.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def write_source(self, file_name, source):
        """ABSTRACT: Write source code to `file_name`

        If source cannot be written for some reason, subclasses should raise
        :class:`CouldNotWriteSourceError`.

        Default implementation raises NotImplementedError.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_files(self):
        """ABSTRACT: Yields relative file paths to all files to be translated.

        The order of yielding of file-names may change but all file names will
        be yielded only once.

        Default implementation raises NotImplementedError.
        """
        raise NotImplementedError()
