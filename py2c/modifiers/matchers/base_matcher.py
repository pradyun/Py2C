"""Implements base class for matchers
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import abc


class BaseMatcher(object, metaclass=abc.ABCMeta):
    """Base class of all matchers
    """

    def __init__(self):
        super().__init__()

    @abc.abstractmethod  # coverage: no partial
    def match(self, node):
        """Match against the node

        Arguments
        ---------
        ``node``
            The node to match against.

        Returns
        -------
            A bool, denoting if the node is a match.

        Matching is based solely on this attribute of the BaseMatcher object.
        This object defines what matches the nodes.
        """
        raise NotImplementedError()

    def generic_match(self, matcher, value):
        """Match the value to matcher

        Arguments
        ---------
        ``matcher``
            The object to match with.
        ``value``
            object to match.

        Returns
        -------
            Whether ``value`` matches with ``matcher``.
        """
        builtin_types = (
            str, bytes, bool, int, float, complex, None.__class__
        )
        if isinstance(matcher, builtin_types):
            return matcher == value
        elif isinstance(matcher, BaseMatcher):
            return matcher.match(value)
        else:
            raise Exception("Unknown matcher: {}".format(matcher))
