"""An Abstract Base Class for Managers
"""

import abc

from py2c.utils import verify_attribute

__all__ = ["Manager"]


class Manager(object, metaclass=abc.ABCMeta):
    """Base class of all managers
    """

    def __init__(self):
        super().__init__()
        verify_attribute(self, "options", dict)

    @abc.abstractmethod  # coverage: no partial
    def run(self, options, *args, **kwargs):
        """Perform the task that manager is supposed to do.

        Arguments:
            options
                A dictionary object with the relavent options passed with
                values.
        """
        raise NotImplementedError()
