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
import re
import ast
import inspect
import collections

from py2c import ast_translator, python_builtins

basic_format = """
### TODO
"""

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

class CompletionCoverageTracker(object):
    """Completion Coverage Tracker

    This class generate the tables on the wiki page that calculates how
    much of the ast and builtins have been implemented."""
    def __init__(self):
        super(CompletionCoverageTracker, self).__init__()
        self.data = []
        self.excluded_nodes = [
            ast.boolop, ast.cmpop, ast.unaryop, ast.operator, ast.mod
        ]
        self.skipped_nodes = [
            ast.AST, ast.alias, ast.arguments, ast.comprehension, ast.expr,
            ast.expr_context, ast.excepthandler, ast.keyword, ast.slice,
            ast.stmt
        ]

    def build_table(self, header, rows):
        def make_row_string(row, width=32):
            row = map(str, map(str, row))
            return '| '+ (' | '.join(map(lambda x: x.center(width), row)))+' |'

        total = len(rows)
        done = len(filter(None, zip(*rows)[1])) # no. of Trues in the rows

        stats = (("Implemented {0} out of {1}".ljust(24)+
                 " ({2:.2%})").format(done, total, float(done)/total))

        header_string = make_row_string([header, stats])
        header_string = '\n'.join([
            header_string,
            re.sub('[^|]', '-', header_string)
            ])

        rows_string = '\n'.join(map(make_row_string, rows))
        return '\n'.join((header_string, rows_string))

    def collect_data(self):
        # Built-in functions
        builtins = []
        for x in dir(__builtins__):
            if x.startswith('_'):
                continue
            obj = getattr(__builtins__, x)
            if (inspect.isclass(obj) and not issubclass(obj, BaseException))\
              or inspect.isbuiltin(obj):
                builtins.append((x, hasattr(python_builtins, x)))
        # AST Nodes - Python to C
        nodes = []
        for name in dir(ast):
            obj = getattr(ast, name)
            if inspect.isclass(obj) and issubclass(obj, ast.AST):
                skip = any(map(lambda x: issubclass(obj, x), self.excluded_nodes))
                skip = skip or obj in self.skipped_nodes
                if skip:
                    continue

                is_covered = hasattr(ast_translator.ASTTranslator, "visit_" + name)
                nodes.append((name, is_covered))

        self.data = (nodes, builtins)

    def build(self):
        self.collect_data()
        table_nodes    = self.build_table("AST nodes", self.data[0])
        table_builtins = self.build_table('Built-in Functions', self.data[1])
        return '\n\n\n'.join((table_builtins, table_nodes))

if __name__ == '__main__':
    print CompletionCoverageTracker().build()
