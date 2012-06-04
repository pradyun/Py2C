from ast import *
import unittest
import converter
class ConverterTest(unittest.TestCase):
    binopcodes = ("((3<<4*45)+4)*(2<<5)","(6*5-3)*(5|5)")
    nobracestree = (("allman",While(body = []),True),)
    childtree = ((For(target=123,body=["test1","test2"],orelse = AST(),iter="test3"),('test3','test1','test2')),)
    def setUp(self):
        self.c = converter.Converter()
    def test_BinOp(self):
        for code in self.binopcodes:
            self.assertEqual(self.c.visit_BinOp(parse(code).body[0].value),code)
    def test_nobraces(self):
        for self.c.style,tree,result in self.nobracestree:
            self.assertEqual(self.c.nobraces(tree),result)
    def test_children(self):
        for tree,result in self.childtree:
            self.assertTrue(all(item == resultitem for item,resultitem in zip(self.c.children(tree),iter(result))))
                 
        
if __name__ == "__main__":
    unittest.main(verbosity = 2)
