#!/usr/bin/python3
"""Tests for the AST used to represent Python and C in one Tree.
"""

#-------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------


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
