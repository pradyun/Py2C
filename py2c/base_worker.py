"""An Abstract Base Class for Workers
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

import abc

__all__ = ["BaseWorker"]


class BaseWorker(object, metaclass=abc.ABCMeta):
    """Base class of all workers
    """

    @abc.abstractmethod  # coverage: no partial
    def work(self, *args, **kwargs):
        """Perform the task that worker is supposed to do.
        """
        raise NotImplementedError()
