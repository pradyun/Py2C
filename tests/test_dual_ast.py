#!/usr/bin/env python
"""Implemetation Tests for the AST system used
"""

import unittest
import py2c.dual_ast as dual_ast


class ASTTestCase(unittest.TestCase):
    """Tests for base tree node class: AST
    """
    def test_equality_1(self):
        """Test for equality for in really equal Nodes
        """

    def test_equality_2(self):
        """Test for equality with node when it has children nodes
        """

    def test_inequality_with_diff_value(self):
        """Test for inequality on nodes with in-equal attributes
        """

    def test_equality_diff_type(self):
        """Test for inequality on the basis of type
        """


if __name__ == '__main__':
    unittest.main()
