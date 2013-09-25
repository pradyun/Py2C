#!/usr/bin/env python
import os
import re
from textwrap import dedent

def indent(string, indent_with='    '):
    return '\n'.join([(indent_with+line)
                             for line in string.strip('\r\n').splitlines()])

class AST(object):
    """Abstract AST Node"""
    def __repr__(self):  # pragma: no cover  No tests (For debugging)
        args = ", ".join(("{0}={1!r}".format(k, getattr(self, k)) for k in self._fields))
        return "{0}({1})".format(self.__class__.__name__, args)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        elif self._fields != other._fields:
            return False
        else:
            for i in self._fields:
                if not hasattr(other, i) or \
                  getattr(self, i) != getattr(other, i):
                    return False
            return True

    def __ne__(self, other):
        return not self == other


#-------------------------------------------------------------------------------
# AST Nodes parser
#-------------------------------------------------------------------------------
class Parser(object):
    """Loads the AST dynamically into classes

    This Parser parses the file passed in through """
    def __init__(self):
        super(Parser, self).__init__()
        self.data = []
        self.func_string = """
        def __init__(self{formed_args}):
            super(self.__class__, self).__init__()
            self._fields = {cleaned_args}
        {setters}
        """
        self.func_string = dedent(self.func_string).strip()

    def prepare(self, f):
        """Prepare the parser for generating classes, from file `f`"""
        try:
            text = f.read()
        except Exception:
            msg = ("Expected file(-like) object with 'read' method, not found "
                   "in object of type {0!r} object".format(type(f)))
            raise TypeError(msg)
        # have got the text by now
        def split_args(li):
            "Splits [object, *attrs] into [object, attrs]"
            args = [map(lambda a: a.strip(), arg.split(','))
                       for i, arg in enumerate(li[1:])]
            return [li[0]] + (args if args and all(*args) else [[]])

        text = re.sub(r"#.*(\n|$)", "", text) # remove comments
        lines = filter(lambda x: len(x) > 1, text.splitlines())
        data = map(lambda x: x.split(':'), lines)
        self.data = map(split_args, data)
        return True

    def setup_module(self, module=None, verbose=False):
        if module is None:
            di = globals()
        elif not isinstance(module, dict):
            di = module.__dict__
        else:
            di = module
        for k, v in self.data:
            cls = self.create_class(k, v, verbose)
            di[k] = cls

    def create_class(self, name, args, verbose):
        if verbose:
            print "class {0}(AST):".format(name)
        __init__ = self.create_init(args, verbose)
        # make something cleanly!!
        cls = type(name, (AST,), {'__init__': __init__})
        return cls

    def create_init(self, args, verbose):
        "Creates the __init__ function from arguments and returns it"
        cleaned_args = '['+(', '.join(repr(x.split('=')[0]) for x in args))+']'
        formed_args = ''.join((', '+x) for x in args)
        setters = indent('\n'.join("self.{0} = {0}".format(i.split('=')[0])
                                                           for i in args))
        di = {}
        string = self.func_string.format(**locals())
        if verbose:
            print indent(string)+'\n\n'
        exec self.func_string.format(**locals()) in di
        return di['__init__']

# Export Nodes
def prepare(module=None, verbose=False):
    p = Parser()
    p.prepare(open(os.path.join(os.path.dirname(__file__), "astnodes.txt")))
    p.setup_module(module, verbose)
