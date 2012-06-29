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
