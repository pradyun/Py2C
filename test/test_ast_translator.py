#!/usr/bin/env python

import ast
import unittest

import support

with support.project_imports():
    import py2c
    import c_ast
    c_ast.prepare()


class ASTTestCase(unittest.TestCase):
    """Abstract TestCase: Tests for C AST translation"""
    longMessage = True # useful!

    def setUp(self):
        self.translator = py2c.ASTTranslator()

    def get_c_ast(self, py_node):
        self.node = py_node
        return self.translator.visit(self.node)

class NumTestCase(ASTTestCase):
    """Tests for translation from Num"""
    def template(self, py_node, check_node, msg):
        "The template for tests in this TestCase"
        msg = "Improper conversion of {0}".format(msg)
        code = self.get_c_ast(py_node)
        self.assertEqual(code, check_node, msg=msg)

    def test_int_negative(self):
        self.template(ast.Num(-1), c_ast.Int(-1), "-ve integer")

    def test_int_positive(self):
        self.template(ast.Num(1), c_ast.Int(1), "+ve integer")

    def test_int_zero(self):
        self.template(ast.Num(0), c_ast.Int(0), "0 (int)")

    def test_float_negative(self):
        self.template(ast.Num(-1.0), c_ast.Float(-1.0), "-ve float")

    def test_float_positive(self):
        self.template(ast.Num(1.0), c_ast.Float(1.0), "+ve float")

    def test_float_zero(self):
        self.template(ast.Num(0.0), c_ast.Float(0.0), "0 (float)")

if __name__ == '__main__':
    unittest.main()
