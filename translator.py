from ast import *
import math
import traceback
import copy
import functools
ordertuple = ((Or,),(And,),(BitOr,),(BitXor,),(BitAnd,),(Eq,NotEq),(LShift,RShift),(Add,Sub),(Div,Mult,Mod))
order = {}
order.update((item,index) for index in range(len(ordertuple)) for item in ordertuple[index])
opdict = {Add:"+",Sub:"-",Div:"/",Mult:"*",LShift:"<<",RShift:">>",Or:"or",BitOr:"|",And:"and",BitAnd:"&",BitXor:"^"}
class Translator(NodeVisitor):
    style = "allman"
    parent = False
    parentop = None
    typedict = {}
    includes = ["sys/types.h"]
    def visit(self,node):
        a = opdict.get(type(node))
        if a is not None:return a
        if not isinstance(node,(BinOp,While,If,Assign,Module,FunctionDef)):
            for field, value in iter_fields(node):
                if isinstance(value,AST):
                    setattr(node,field,self.visit(value))
                elif isinstance(value,list):
                    setattr(node,field,[self.visit(child) for child in value])
        return super().visit(node)
    def children(self,node):
        for fields in node._fields:
            value = getattr(node,fields)
            if isinstance(value,str):yield value
            elif isinstance(value,list):
                for child in value:
                    yield child
    def convert_args_or_test(args_on_test):return "("+",".join(args_or_test)+")"
    @functools.lru_cache()
    def nobraces(self,node):
        if hasattr(node,"body"):
                if self.style == "allman":return len(node.body)<=1 and all(map(self.nobraces,node.body))
        return True
    def generic_block(self,node,name,args_or_test):
        nobraces = self.nobraces(node)
        return "".join((name," (",args_or_test,")"," "  if nobraces else "\n{\n",\
                        "\n".join("    "+self.visit(child)+("" if hasattr(child,"body") else ";") for child in node.body)," " if nobraces else "\n}"))
    def loop_block(self,node):
        return self.generic_block(node,node.__class__.__name__.lower(),self.visit(node.test))
    def ctype(self,node):
        #if isinstance(node,BinOp):return ctype(classdict[addenode.left].__add__ or node.right.__radd__)
        if isinstance(node,Name):return typedict[node.id]
        if isinstance(node,Num):return ("char","short","int","long","long long")[((node.n.bit_length()-1)//8).bit_length()]
        if isinstance(node,Tuple):return self.ctype(node.elts[0])
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
        s = "".join(map(self.visit,(node.left,node.op,node.right)))
        self.parentop = oldparent
        if self.parentop is not None and order[type(node.op)] < order[type(self.parentop)]:
            s = "("+s+")"
        return s
    def visit_Assign(self,node):
        return self.ctype(node.value)+" "+" = ".join(map(self.visit,node.targets+[node.value]))
    def visit_Tuple(self,node):return ",".join(node.elts)
    def visit_Num(self,node):return str(node.n)
    def visit_Name(self,node):return node.id.lower() if node.id in ("True","False") else node.id
    def visit_Return(self,node):return "return "+node.value
    def visit_FunctionDef(self,node):
        return self.generic_block(node,"type_xxx"+" "+node.name,"false args")
    def visit_Call(self,node):
        if node.keywords != [] or node.starargs is not None or node.kwargs is not None:
            raise NotImplementedError("Keyword and starred arguments are not implemented in PyToC")
        return node.func+self.convert_args_or_test(node.args)
    def generic_visit(self,node):
        self.parent = self.children(node)
        return "".join(self.parent)
import pytoc
