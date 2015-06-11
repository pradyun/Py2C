"""An Abstract Base Class for Workers
"""

import abc
import logging

__all__ = ["Worker"]


class Worker(object, metaclass=abc.ABCMeta):
    """ABC for Workers
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
