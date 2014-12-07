"""Implements an attribute-based Matcher.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from .base_matcher import BaseMatcher


class Attributes(BaseMatcher):
    """Matches if attributes of an object are same as those passed during \
    initalization of an instance of this class.
    """

    def __init__(self, attrs):
        self._attrs = attrs

    def match(self, node):
        placeholder = object()
        for name, value in self._attrs.items():
            attr = getattr(node, name, placeholder)
            if attr is placeholder or not self.generic_match(value, attr):
                return False
        return True
