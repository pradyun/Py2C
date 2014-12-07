"""An Abstract Base Class for Modifiers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import abc

from py2c.utils import verify_attribute
from py2c.modifiers.matchers.base_matcher import BaseMatcher


class BaseModifier(object, metaclass=abc.ABCMeta):
    """Base class of all modifiers
    """

    def __init__(self):
        super().__init__()
        verify_attribute(self, "matcher", BaseMatcher)

    @abc.abstractmethod  # coverage: no partial
    def modify(self, node):
        """Modify the tree node

        Arguments:
            node
                A node that the Matcher matched sucessfully with.

        Returns:
            A replacement value (AST node, list containing AST nodes etc),
            that replaces the node passed.
        """
        raise NotImplementedError()
