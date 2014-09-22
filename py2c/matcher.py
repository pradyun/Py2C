"""Implements matchers for the modifiers
"""
import abc


class Matcher(object, metaclass=abc.ABCMeta):
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

        Matching is based solely on this attribute of the Matcher object.
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
        built_in_types = (str, bytes, bool, int, float, complex, None.__class__)
        if isinstance(matcher, built_in_types):
            return matcher == value
        elif isinstance(matcher, Matcher):
            return matcher.match(value)
        else:
            print("Unknown matcher: {}".format(matcher))
            return False


class Instance(Matcher):
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


class Attributes(Matcher):
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
