import sys
from ast import *
HAS_LONG_LONG = sys.maxsize.bit_length() == 63
class c_type:
    def __init__(self,pointer = False):
        self.pointer = pointer
    def to_str(self):return self.string+("*" if self.pointer else "")
class c_integer(c_type):
    #def __init__(self,size,sign = False,pointer = False):
    #   self.sign = sign
    #    self.size = size
     #   self.pointer = pointer
    string = "signed long long" if HAS_LONG_LONG else "signed long"
    #return ("un" if self.sign else "")+ "signed " + ("char","short","int","long","long long")[self.size]
class c_void(c_type):
    def __init__(self,pointer = False):
        self.pointer = pointer
    string = "void"
class c_func(c_type):
    def __init__(self,return_type,pointer = False):
        self.return_type = return_type
        self.pointer = pointer
        string = self.return_type.string
#class c_union:
    #def __init__(self,types):
def ctype(node):
        '''Finds the C/C++ type of the node'''
        #if isinstance(node,BinOp):return ctype(classdict[addenode.left].__add__ or node.right.__radd__)
        if isinstance(node,Name):return self.typedict[node.id]
        if isinstance(node,Num):return c_integer(((node.n.bit_length()-1)//8).bit_length())
        if isinstance(node,Tuple):return self.ctype(node.elts[0])
        if isinstance(node,set):
            for item in iter(node):return item
        raise TypeError("invalid type for node {}".format(type(node)))
