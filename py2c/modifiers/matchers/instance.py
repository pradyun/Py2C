"""Implements an isinstance-based Matcher.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from .base_matcher import BaseMatcher
from .attributes import Attributes


class Instance(BaseMatcher):
    """Matches if object isinstance of the class passed initially.
    """

    def __init__(self, cls, attrs=None):
        super().__init__()
        self._cls = cls
        if attrs is not None:
            self._attrs = Attributes(attrs)
        else:
            self._attrs = None

    def match(self, node):
        if not isinstance(node, self._cls):
            return False
        elif self._attrs is not None:
            return self._attrs.match(node)
        else:
            return True

