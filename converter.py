from ast import *
import traceback
import copy
ordertuple = ((Or,),(And,),(BitOr,),(BitXor,),(BitAnd,),(Eq,NotEq),(LShift,RShift),(Add,Sub),(Div,Mult,Mod))
order = {}
order.update((item,index) for index in range(len(ordertuple)) for item in ordertuple[index])
opdict = {Add:"+",Sub:"-",Div:"/",Mult:"*",LShift:"<<",RShift:">>",Or:"or",BitOr:"|",And:"and",BitAnd:"&",BitXor:"^"}
                
class Converter(NodeVisitor):
    style = "allman"
    parent = False
    parentop = None
    def visit(self,node):
        a = opdict.get(type(node))
        if a is not None:return a
        if not isinstance(node,(BinOp,While,If)):
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
    def nobraces(self,node):
        if hasattr(node,"body"):
                if self.style == "allman":return len(node.body)<=1 and all(map(self.nobraces,node.body))
        return True
    def block(self,node):
        nobraces = self.nobraces(node)
        return "".join((node.__class__.__name__.lower()," (",self.visit(node.test),")"," "  if nobraces else "\n{\n",\
                        "".join("    "+self.visit(child)+("" if hasattr(child,"body") else ";")+"\n" for child in node.body)[:-1]," " if nobraces else "\n}"))
    
    visit_While = block
    visit_If = block

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
    def visit_Assign(self,node):return "=".join(node.targets+[node.value])
    def visit_Tuple(self,node):return ",".join(node.elts)
    def visit_Num(self,node):return str(node.n)
    def visit_Name(self,node):return node.id.lower() if node.id in ("True","False") else node.id
    def visit_Call(self,node):
        if node.keywords != [] or node.starargs is not None or node.kwargs is not None:
            raise NotImplementedError("Keyword and starred arguments are not implemented in PyToC")
        return node.func+"("+",".join(node.args)+")"
    def generic_visit(self,node):
        return "".join(children(node))
