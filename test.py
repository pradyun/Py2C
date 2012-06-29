__author__ = "Ramchandra Apte <maniandram01@gmail.com>"
__license__ = '''
Copyright (C) 2012 Ramchandra Apte <maniandram01@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License at LICENSE.txt for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from ast import *
import unittest
import translator
class TranslatorTest(unittest.TestCase):
    class examples:
        binop = ("((3<<4*45)+4)*(2<<5)","(6*5-3)*(5|5)")
        nobraces = (("allman",While(body = []),True),)
        children = ((For(target=123,body=["test1","test2"],orelse = AST(),iter="test3"),('test3','test1','test2')),)
        tuple_unpacking = ()
    c = translator.Translator()
    def test_BinOp(self):
        #TODO do not parse code instead make it ast branches
        for code in self.examples.binop:
            self.assertEqual(self.c.visit_BinOp(parse(code).body[0].value),code)
    def test_nobraces(self):
        for self.c.style,tree,result in self.examples.nobraces:
            self.assertEqual(self.c.nobraces(tree),result)
    def test_children(self):
        for tree,result in self.examples.children:
            self.assertTrue(all(item == resultitem for item,resultitem in zip(self.c.children(tree),result)))
    def test_tuple_unpacking(self):
        for tree,result in self.examples.tuple_unpacking:
            #NOTE: Do not use visit_Assign
            self.assertEqual(self.c.visit(tree),result)
if __name__ == "__main__":
    unittest.main(verbosity = 2)
