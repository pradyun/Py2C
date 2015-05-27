"""Type inference using constraints.
"""

from py2c.base_worker import BaseWorker
from py2c.tree.visitors import RecursiveNodeVisitor


class TypeAnalyser(BaseWorker, RecursiveNodeVisitor):
    """Analyses the FlowTree for finding type constraints on level 1 variables.
    """

    def work(self, node):
        # Infer constraints on the variables, based on the AST
        self.visit(node)
