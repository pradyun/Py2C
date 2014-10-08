"""Implements an Abstract Base Class for Modifiers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import abc
from . import matcher


class Modifier(object, metaclass=abc.ABCMeta):
    """Base class of all modifier
    """

    def __init__(self):
        super().__init__()
        if not hasattr(self, "matcher"):
            raise AttributeError(
                "{} should have a matcher attribute.".format(
                    self.__class__.__qualname__
                )
            )
        elif not isinstance(self.matcher, matcher.Matcher):
            raise TypeError(
                "{}.matcher should be an instance of a subclass of {}".format(
                    self.__class__.__qualname__,
                    matcher.Matcher.__class__.__qualname__
                )
            )

    @abc.abstractmethod  # coverage: no partial
    def modify(self, node):
        """Modify the tree node

        Arguments:
            node
                A node that the Matcher matched sucessfully with.

        Returns:
            A replacement value (node), that is placed in-place of the node
            passed.
        """
        raise NotImplementedError()
