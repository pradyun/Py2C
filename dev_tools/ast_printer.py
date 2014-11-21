"""This is a really dirty script that is used to dump the AST.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import ast
import py2c.syntax_tree

import py2c.syntax_tree.python as py


class Indentor(object):
    """A simple class to manage indents
    """

    def __init__(self, indent_with='    '):
        self.indent = ""
        self._indent_with = indent_with
        self.skip = False

    def should_skip_next(self, should=True):
        self.skip = should

    def __enter__(self):
        self.indent = self.indent + self._indent_with

    def __exit__(self, *args):
        self.indent = self.indent[:-len(self._indent_with)]

    def __str__(self):
        if self.skip:
            self.skip = False
            return ""
        else:
            return self.indent


def write(*args, sep="", end=""):
    print(*args, sep=sep, end=end)


def _dump(node, indentor):
    if isinstance(node, (list, tuple)):
        _dump_list(node, indentor)
    elif isinstance(node, (py2c.syntax_tree.AST, ast.AST)):
        _dump_node(node, indentor)
    else:
        write(indentor, repr(node))


def _dump_list(li, indentor):
    if not li:
        write("[]")
        indentor.skip = False
    else:
        length = len(li)
        write("[")
        for i, elem in enumerate(li):
            with indentor:
                write("\n")
                indentor.skip = False
                _dump(elem, indentor)
            if i < length - 1:
                write(",")

        should_skip = indentor.skip
        write("\n", indentor, "]")
        indentor.skip = should_skip


def _dump_node(node, indentor):
    # Initial header
    if isinstance(node, py2c.syntax_tree.AST):
        module = "py"
        iter_fields = py2c.syntax_tree.iter_fields
    else:
        module = "ast"
        iter_fields = ast.iter_fields
    write(indentor, "{}.{}(".format(module, node.__class__.__name__))

    # Should the node be printed inline
    in_line = isinstance(node, (py.Name, py.NameConstant, ast.Name, ast.NameConstant))
    length = len(node._fields)
    for i, (name, value) in enumerate(iter_fields(node)):
        with indentor:
            if in_line:
                indentor.skip = True
            else:
                write("\n")
            write(indentor, name, "=")
            indentor.skip = True
            _dump(value, indentor)
            if i < length - 1:
                write(",")
                if in_line:
                    write(" ")
    if not in_line and node._fields:
        write("\n", indentor, ")",)
    else:
        write(")")


#------------------------------------------------------------------------------
# Final stuff
#------------------------------------------------------------------------------
def dump_ast(node, indent_with="   "):
    return _dump(node, Indentor())


def main():
    import textwrap
    dump_ast(ast.parse(textwrap.dedent("""
        if a > b:
            pass
    """)))

if __name__ == '__main__':
    main()
