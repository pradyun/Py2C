"""Type inference using constraints.
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

from py2c.analysis.base_analyser import BaseAnalyser


class TypeAnalyser(BaseAnalyser):
    """Analyses the FlowTree for inferring types.
    """

    def analyse(self, node):
        self.node = node
        # Infer constraints on the unknown variables,
        # Based on the AST and provided types
        self.infer_constraints()
        # Solve the inferred constraints, raising errors if conflicting constraints exist (due to invalid user input)
        self.solve_constraints()

    def infer_constraints(self):
        raise NotImplementedError()

    def solve_constraints(self):
        raise NotImplementedError()
