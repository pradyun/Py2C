"""An Abstract Base Class for Workers
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

import abc
import logging

__all__ = ["BaseWorker"]


class BaseWorker(object, metaclass=abc.ABCMeta):
    """Base class of all workers
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__qualname__)
        self._setup_logger()

    def _setup_logger(self):
        formatter = logging.Formatter(
            "{levelname} {asctime} {filename}:{lineno} '{message}'",  # noqa
            "%d-%m-%Y@%H:%M:%S",
            "{"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    @abc.abstractmethod  # coverage: no partial
    def work(self, *args, **kwargs):
        """Perform the task that worker is supposed to do.
        """
        raise NotImplementedError()
