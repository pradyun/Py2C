"""BaseNodeVisitor and it's concrete subclasses
"""

import abc
import collections

from py2c.tree import Node, iter_fields


__all__ = ["RecursiveNodeVisitor", "RecursiveNodeTransformer"]


# -----------------------------------------------------------------------------
# Base Class of NodeVisitors
# -----------------------------------------------------------------------------
class BaseNodeVisitor(object, metaclass=abc.ABCMeta):
    """A base class for NodeVisitors
    """

    # Serves as a stub when a function needs to return None
    NONE_DEPUTY = object()

    # Arguments allow reuse with similar but different Node systems.
    # For example, these visitors are compatible with `ast`, even though they
    # don't need to be.
    def __init__(self, base_class=Node, iter_fields=iter_fields):
        super().__init__()
        self.base_class = base_class
        self.iter_fields = iter_fields

    def visit(self, node):
        """Visits a node.
        """
        return self._visit(node)

    def _visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)

        return visitor(node)

    @abc.abstractmethod
    def generic_visit(self, node):
        self._visit_children(node)

    @abc.abstractmethod
    def _visit_children(self, node):  # coverage: not missing
        raise NotImplementedError()

    def _visit_value(self, parent, field, value, index=None):
        val = self._visit(value)
        return val


# -----------------------------------------------------------------------------
# Concrete sub-classes of BaseNodeVisitor
# -----------------------------------------------------------------------------
class RecursiveNodeVisitor(BaseNodeVisitor):
    """Visits the base nodes before parent nodes.
    """

    def generic_visit(self, node):
        super().generic_visit(node)

    def _visit_children(self, node):
        for field, value in self.iter_fields(node):

            value = getattr(node, field, None)

            if isinstance(value, list):
                self._visit_list(node, field, value)
            elif isinstance(value, self.base_class):
                self._visit_value(node, field, value)

    def _visit_list(self, node, field, original_list):
        for i, value in enumerate(original_list):
            if isinstance(value, self.base_class):
                self._visit_value(node, field, value, i)


# TEST:: Write tests once I know how this is supposed to be used.
class RecursiveNodeTransformer(BaseNodeVisitor):
    """A BaseNodeVisitor that allows modification of Nodes, in-place.

    RecursiveNodeTransformer walks the Node and uses the return value of the
    visitor methods to replace or remove the Nodes.

    If the return value of the visitor method is:
      1. `None`: The node will be removed from its location
      2. `self.NONE_DEPUTY`: The node will be replaced with `None`
    Otherwise the node is replaced with the return value.
    The return value may be the original node in which case no replacement
    takes place.

    Based off `ast.NodeTransformer`
    """

    def visit(self, node):
        retval = super().visit(node)
        if retval is self.NONE_DEPUTY:
            retval = None
        return retval

    def generic_visit(self, node):
        super().generic_visit(node)
        return node

    def _visit_children(self, node):
        """Visit all children of node.
        """
        for field, old_value in self.iter_fields(node):
            if isinstance(old_value, list):
                self._visit_list(node, field, old_value)
            elif isinstance(old_value, self.base_class):
                new_node = self._visit_value(node, field, old_value)

                if new_node is None:
                    delattr(node, field)
                else:
                    if new_node is self.NONE_DEPUTY:
                        new_node = None

                    setattr(node, field, new_node)

    # Moved out of '_visit_children' for readability
    def _visit_list(self, node, field, original_list):
        new_list = []
        for i, value in enumerate(original_list):
            if isinstance(value, self.base_class):
                value = self._visit_value(node, field, value, i)

                if value is None:
                    continue
                elif value is self.NONE_DEPUTY:
                    # This is invalid in this py2c.tree system
                    value = None  # coverage: not missing
                elif isinstance(value, collections.Iterable):
                    new_list.extend(value)
                    continue

            new_list.append(value)

        original_list[:] = new_list
