#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Contains matchers for the modifiers
"""
import abc


class Matcher(object, metaclass=abc.ABCMeta):
    """Base class of all matchers
    """
    def __init__(self):
        super().__init__()
        self._name_stack = []

    @abc.abstractmethod  # coverage: no partial
    def matches(self, node):
        """Match against the node

        Arguments
        ---------
        ``node``
            The node to match against.

        Returns
        -------
            A bool, denoting if the node is a match.
        """

    def match(self, matcher, value):
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
        built_in_types = (str, bytes, bool, int, float, complex, None.__class__)
        if isinstance(matcher, built_in_types):
            return matcher == value
        elif isinstance(matcher, Matcher):
            return matcher.matches(value)
        else:
            print("Unknown matcher: {}".format(matcher))
            return False


class Instance(Matcher):
    """Matches an instance of a class
    """
    def __init__(self, cls, attrs={}):
        super().__init__()
        self._cls = cls
        self._attrs = attrs

    def matches(self, node):
        if not isinstance(node, self._cls):
            return False
        placeholder = object()
        for name, value in self._attrs.items():
            attr = getattr(node, name, placeholder)
            if attr == placeholder or not self.match(value, attr):
                return False
        return True
