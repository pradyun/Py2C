#!/usr/bin/env python
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
newline = LazyString("\n")
ordertuple = ((Or,),(And,),(BitOr,),(BitXor,),(BitAnd,),(Eq,NotEq),(LShift,RShift),(Add,Sub),(Div,Mult,Mod))
order = {}
order.update((item,index) for index in range(len(ordertuple)) for item in ordertuple[index])
opdict = {Add:"+",Sub:"-",Div:"/",Mult:"*",LShift:"<<",RShift:">>",Or:"or",BitOr:"|",And:"and",BitAnd:"&",BitXor:"^"}


# class Translator(NodeVisitor):
#     style = "allman"
#     parent = False
#     parentop = None
#     typedict = {}
#     includes = ["testinclude.h"]
    
#     def visit(self,node):
#         '''Customised visit() .'''
#         a = opdict.get(type(node))
#         if a is not None:return a
#         if not isinstance(node,(BinOp,While,If,Assign,Module,FunctionDef,Return,Call)):
#             for field, value in iter_fields(node):
#                 if isinstance(value,AST):
#                     setattr(node,field,self.visit(value))
#                 elif isinstance(value,list):
#                     setattr(node,field,[self.visit(child) for child in value])
#         string = super().visit(node)
#         if isinstance(string,LazyString):string.vars_ = self.typedict
#         return string
    
#     def children(self,node):
#         '''Find children of node which are LazyString instances.'''
#         for fields in node._fields:
#             value = getattr(node,fields)
#             if isinstance(value,str):yield value
#             elif isinstance(value,list):
#                 for child in value:
#                     yield child
                    
#     def convert_args_or_test(self,args_or_test):
#         '''Converts args or test into a LazyString.'''
#         return LazyString(",").join(args_or_test)
    
#     @functools.lru_cache()
#     def nobraces(self,node):
#         '''Finds out if the node requires no braces.'''
#         if hasattr(node,"body"):
#                 if self.style == "allman":return len(node.body)<=1 and all(map(self.nobraces,node.body))
#         return True
    
#     def generic_block(self,node,name,args_or_test):
#         '''Converts a block node to a string.'''
#         #TODO don't give four spaces for Pass()
#         nobraces = self.nobraces(node)
#         return empty.join ( (name," (",args_or_test,")"," "  if nobraces else "\n{\n",\
#                         newline.join("    "+self.visit(child)+("" if hasattr(child,"body") else ";") for child in node.body)," " if nobraces else "\n}"))
    
#     def loop_block(self,node):
#         '''Converts a loop block node to a string.'''
#         return self.generic_block(node,node.__class__.__name__.lower(),self.visit(node.test))

#     visit_While = loop_block
#     visit_If = loop_block

#     def visit_Module(self,node):
#         return empty.join("#include <"+filename+">"+"\n" for filename in self.includes)+newline.join(self.visit(child)+("" if hasattr(child,"body") else ";") for child in node.body)
#     def visit_Pass(self,node):
#         return ""
#     def visit_BinOp(self,node):
#         if self.parent is False:
#             self.parentop = None
#         self.parent = True
#         oldparent = self.parentop
#         self.parentop = node.op
#         s = "".join(map(self.visit,(node.left,node.op,node.right)))
#         self.parentop = oldparent
#         if self.parentop is not None and order[type(node.op)] < order[type(self.parentop)]:
#             s = "("+s+")"
#         return s
    
#     def visit_Assign(self,node):
#         type_ = ctype(node.value)
#         if isinstance(node.targets[0],Tuple):
#             targets = node.targets[0]
#         else:
#             targets = node.targets
#         for name in targets:self.typedict[name.id] = type_
#         return type_.to_str()+" "+" = ".join(map(self.visit,node.targets+[node.value]))
    
#     def visit_Tuple(self,node):return ",".join(node.elts)
#     def visit_Num(self,node):return str(node.n)
#     def visit_Name(self,node):return node.id.lower() if node.id in ("True","False") else node.id
#     def visit_Return(self,node):
#         return "return "+self.visit(node.value)
    
#     def visit_FunctionDef(self,node):
#         for stmt in node.body:
#             if isinstance(stmt,Return):
#                 returnvalue = ctype(stmt.value)
#                 break
#         else:returnvalue = c_void()
#         self.typedict[node.name] = c_func(returnvalue)
#         return self.generic_block(node,returnvalue.to_str()+" "+node.name,self.convert_args_or_test(LazyString(Variable(arg.arg)," ",arg.arg) for arg in node.args.args))
    
#     def visit_Call(self,node):
#         if node.keywords != [] or node.starargs is not None or node.kwargs is not None:
#             raise NotImplementedError("Keyword and starred arguments are not implemented in PyToC")
#         self.typedict
#         print(node.args)
#         return node.func+self.convert_args_or_test(map(self.visit,node.args))
    
#     def generic_visit(self,node):
#         self.parent = self.children(node)
#         return empty.join(self.parent)

#remove after development
if __name__ == "__main__":
    
    import py2c
