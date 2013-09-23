#!/usr/bin/env python
import os
import re
import types
import inspect
from textwrap import dedent

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


#-------------------------------------------------------------------------------
# AST Nodes parser
#-------------------------------------------------------------------------------
class Parser(object):
    """Loads the AST dynamically into classes"""
    def __init__(self):
        super(Parser, self).__init__()
        self.data = []
        self.func_string = """
        def __init__(self{formed_args}):
            super(self.__class__, self).__init__()
            self._fields = {clean_args}
            for x in self._fields:
                setattr(self, x, locals()[x])"""
        self.func_string = dedent(self.func_string)

    def prepare(self, f):
        """Prepare the parser for generating classes, from file `f`"""
        try:
            text = f.read()
        except Exception:
            msg = "Expected file-like object, got {0!r} object".format(type(f))
            raise TypeError(msg)
        # have got the text by now
        def split_args(li):
            "Splits [object, *attrs] into [object, [*attrs]]"
            args = [map(lambda a: a.strip(), arg.split(','))
                       for i, arg in enumerate(li[1:])]
            return [li[0]] + (args if args and all(*args) else [[]])

        text = re.sub(r"#.*\n?", "", text) # remove comments
        lines = filter(lambda x: len(x) > 1, text.splitlines())
        data = map(lambda x: x.split(':'), lines)
        self.data = map(split_args, data)
        return True

    def setup_module(self, module=None):
        if module is None:
            di = globals() # pragma: no cover  Doesn't need to be tested
        elif not isinstance(module, dict):
            di = module.__dict__
        else:
            di = module
        for k, v in self.data:
            cls = self.create_class(k, v)
            di[k] = cls

    def create_class(self, name, args):
        clean_args = self.clean_arguments(args)
        formed_args = self.form_args(args)
        func_string = self.func_string.format(**locals())
        exec func_string
        cls = type(name, (AST,), {'__init__': __init__})
        return cls

    def clean_arguments(self, args):
        return '['+(', '.join(repr(x.split('=')[0]) for x in args))+']'

    def form_args(self, args):
        return ''.join((', '+x) for x in args)

# Export Nodes
def prepare(module=None): # pragma: no cover  Doesn't need to be tested
    p = Parser()
    p.prepare(open(os.path.join(os.path.dirname(__file__), "astnodes.txt")))
    p.setup_module(module)
