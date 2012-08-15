from collections import UserString
from copy import copy
class UserString(UserString):
    '''Monkeypatches UserString.join() to work with a sequence of UserString'''
    #TODO make this more optimized
    def join(self, seq):
        seq = iter(seq)
        try:first = next(seq)
        except StopIteration:return empty
        else:return first+sum((self+item for item in seq),empty)

#TODO add repr for Variable and Str (create Str)
class Variable(str):pass
class LazyString(UserString):
    vars_ = {}
    def __getattr__(self,name):
        if name == "data":return str(self)
        #TODO add proper error message
        else:raise AttributeError("no attribute called '{}'".format(name))
    def __init__(self,*parts):
        self.parts = list(parts)
    def __str__(self):
        return "".join(self.vars_[value].to_str() if isinstance(value,Variable) else value for value in self.parts)
    def __repr__(self):return "{}({})".format(self.__class__.__name__,self.parts)
    #TODO implement faster __iadd__ (current method is slow - calls __add__)
    def __add__(self,other):
        if isinstance(other,self.__class__):return self.__class__(*(self.parts+other.parts))
        else:
            assert isinstance(other,str)
            return self.__class__(*(self.parts+[other]))
    def __radd__(self,other):
        if isinstance(other,self.__class__):return self.__class__(*(other.parts+self.parts))
        else:
            assert isinstance(other,str)
            return self.__class__(*([other]+self.parts))
empty = LazyString()
