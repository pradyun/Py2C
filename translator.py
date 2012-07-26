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
import functools
from c_types import *
from lazystring import *
#constant data
empty = LazyStrin
ordertuple = ((Or,),(And,),(BitOr,),(BitXor,),(BitAnd,),(Eq,NotEq),(LShift,RShift),(Add,Sub),(Div,Mult,Mod))
order = {}
order.update((item,index) for index in range(len(ordertuple)) for item in ordertuple[index])
opdict = {Add:"+",Sub:"-",Div:"/",Mult:"*",LShift:"<<",RShift:">>",Or:"or",BitOr:"|",And:"and",BitAnd:"&",BitXor:"^"}

class Translator(NodeVisitor):
    style = "allman"
    parent = False
    parentop = None
    typedict = {}
    includes = ["testinclude.h"]
    returnvalues = set()
    
    def visit(self,node):
        '''Customised visit() .'''
        a = opdict.get(type(node))
        if a is not None:return a
        if not isinstance(node,(BinOp,While,If,Assign,Module,FunctionDef,Return)):
            for field, value in iter_fields(node):
                if isinstance(value,AST):
                    setattr(node,field,self.visit(value))
                elif isinstance(value,list):
                    setattr(node,field,[self.visit(child) for child in value])
        return super().visit(node)
    
    def children(self,node):
        '''Find children of node which are LazyString instances.'''
        for fields in node._fields:
            value = getattr(node,fields)
            if isinstance(value,str):yield value
            elif isinstance(value,list):
                for child in value:
                    yield child
                    
    def convert_args_or_test(self,args_on_test):
        '''Converts args or test into a LazyString.'''
        return "("+",".join(args_or_test)+")"
    
    @functools.lru_cache()
    def nobraces(self,node):
        '''Finds out if the node requires no braces.'''
        if hasattr(node,"body"):
                if self.style == "allman":return len(node.body)<=1 and all(map(self.nobraces,node.body))
        return True
    
    def generic_block(self,node,name,args_or_test):
        '''Converts a block node to a string.'''
        nobraces = self.nobraces(node)
        return "".join((name," (",args_or_test,")"," "  if nobraces else "\n{\n",\
                        "\n".join("    "+self.visit(child)+("" if hasattr(child,"body") else ";") for child in node.body)," " if nobraces else "\n}"))
    
    def loop_block(self,node):
        '''Converts a loop block node to a string.'''
        return self.generic_block(node,node.__class__.__name__.lower(),self.visit(node.test))
    def ctype(self,node):
        '''Finds the C/C++ type of the node'''
        #if isinstance(node,BinOp):return ctype(classdict[addenode.left].__add__ or node.right.__radd__)
        if isinstance(node,Name):return self.typedict[node.id]
        if isinstance(node,Num):return c_integer(((node.n.bit_length()-1)//8).bit_length())
        if isinstance(node,Tuple):return self.ctype(node.elts[0])
        if isinstance(node,set):
            for item in iter(node):return item
        raise TypeError("invalid type for node {}".format(type(node)))

    visit_While = loop_block
    visit_If = loop_block

    def visit_Module(self,node):
        return "".join("#include <"+filename+">"+"\n" for filename in self.includes)+"\n".join(self.visit(child)+("" if hasattr(child,"body") else ";") for child in node.body)
    def visit_Pass(self,node):return ""
    def visit_BinOp(self,node):
        if self.parent is False:self.parentop = None
        self.parent = True
        oldparent = self.parentop
        self.parentop = node.op
        s = LazyString("").join(map(self.visit,(node.left,node.op,node.right)))
        self.parentop = oldparent
        if self.parentop is not None and order[type(node.op)] < order[type(self.parentop)]:
            s = "("+s+")"
        return s
    
    def visit_Assign(self,node):
        type_ = self.ctype(node.value)
        if isinstance(node.targets[0],Tuple):
            targets = node.targets[0]
        else:
            targets = node.targets
        for name in targets:self.typedict[name.id] = type_
        return type_.to_str()+" "+" = ".join(map(self.visit,node.targets+[node.value]))
    
    def visit_Tuple(self,node):return ",".join(node.elts)
    def visit_Num(self,node):return str(node.n)
    def visit_Name(self,node):return node.id.lower() if node.id in ("True","False") else node.id
    def visit_Return(self,node):
        print(node.value)
        self.returnvalues.add(self.ctype(node.value))
        return "return "+self.visit(node.value)
    def visit_FunctionDef(self,node):
        iterator = iter(self.returnvalues)
        try:returnvalue = next(iterator)
        except StopIteration:returnvalue = c_void()
        return self.generic_block(node,returnvalue.to_str()+" "+node.name,LazyString(Variable("d")))
    def visit_Call(self,node):
        if node.keywords != [] or node.starargs is not None or node.kwargs is not None:
            raise NotImplementedError("Keyword and starred arguments are not implemented in PyToC")
        return node.func+self.convert_args_or_test(node.args)
    def generic_visit(self,node):
        self.parent = self.children(node)
        return "".join(self.parent)
#remove after development
if __name__ == "__main__":
    import py2c
