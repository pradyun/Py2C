#!/usr/bin/env python
"""Work needs to be done on this one!"""
import ast
import inspect
from py2c import dual_ast


__all__ = ["Py2DualTranslator", "dual_ast"]


class Py2DualTranslator(ast.NodeVisitor):
    """Translates Python AST into dual AST

    This is a NodeVisitor that visits the Python AST validates it for conversion
    and creates another AST with type definitions and other stuff, from which
    code is generated.

    Attributes:
        errors: A list that contains the error-messages that of errors that
                occurred during translation.
    """
    def __init__(self):
        super(Py2DualTranslator, self).__init__()
        self.setup()

    def setup(self):
        self.errors = []

    # Errors
    def log_error(self, msg, node=None):
        stack = inspect.stack()
        if len(stack) > 1:
            caller_name = stack[1][3]
            # remove 'visit_'
            if caller_name.startswith('visit_'):
                caller_name = caller_name[6:]
            else:  # If it is not a visit_xxx, don't use it
                caller_name = None
        else:
            # Excluded as this can't be achieved during testing.
            caller_name = None  # pragma : no cover

        if caller_name is not None:
            msg = "(Node type: {0}) {1}".format(caller_name, msg)
        if hasattr(node, "lineno"):
            msg += "Check Line ({0}): {1}".format(node.lineno, msg)
        self.errors.append(msg)

    def print_errors(self):
        if not self.errors:
            return

        print("Error(s) occurred while translating Python AST into dual AST")
        for msg in self.errors:
            print(' - '+msg)

    def get_node(self, node):
        """Get the dual AST from the Python AST `node`
        Args:
            node: The Python AST to be converted to dual AST
        Returns:
            A dual node, from the dual_ast.py or None if there are errors.
        """
        self.setup()
        retval = self.visit(node)
        if self.errors:
            self.print_errors()
            retval = None
        return retval

    # Modified to return values
    def generic_visit(self, node):  # pragma : no cover
        """Called if no explicit visitor function exists for a node."""
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                li = []
                for item in value:
                    if isinstance(item, ast.AST):
                        li.append(self.visit(item))
                return li
            elif isinstance(value, ast.AST):
                return self.visit(value)

    def body(self, body):
        return list(map(self.visit, body))

    def visit_Module(self, node):
        return dual_ast.Module(self.body(node.body))

    # Constants or Variable names
    def visit_Name(self, node):
        return dual_ast.Name(id=node.id, ctx=self.visit(node.ctx))

    def visit_Str(self, node):
        return dual_ast.Str(s=node.s)

    def visit_Num(self, node):
        if isinstance(node.n, int):
            return dual_ast.Int(n=node.n)
        elif isinstance(node.n, float):
            return dual_ast.Float(n=node.n)
        else:
            msg = "Only ints and floats supported, {0} numbers not supported"
            self.log_error(msg.format(node.n.__class__.__name__))

    def visit_Print(self, node, py3=False):
        if py3:  # 'print' function call
            keywords = {}
            if node.keywords is not None:
                for kw in node.keywords:
                    keywords[kw.arg] = kw.value

            sep = keywords.pop('sep', ast.Str(' ')).s
            end = keywords.pop('end', ast.Str('\n')).s
            dest = keywords.pop('file', None)
            if keywords:
                self.log_error(
                    "Unexpected arguments to `print` function call", node
                )
                return None
            if dest is not None:
                dest = self.visit(dest)
            values = map(self.visit, node.args)
        else:
            sep = ' '
            end = '\n' if node.nl else ' '
            dest = node.dest
            if dest is not None:
                dest = self.visit(dest)
            values = map(self.visit, node.values)
        values = list(values)
        return dual_ast.Print(dest=dest, values=values, sep=sep, end=end)

    def visit_Call(self, node):
        if node.func.id == 'print':  # Python 3 print
            return self.visit_Print(node, True)

        if node.keywords:
            self.log_error("Calls with keyword arguments not supported", node)
            return
        if not (node.starargs is None and node.kwargs is None):
            self.log_error("Calls with starred arguments not supported", node)
            return

        func = self.visit(node.func)
        args = list(map(self.visit, node.args))

        return dual_ast.Call(func=func, args=args)

    # Context
    def visit_AugLoad(self, node):
        return dual_ast.AugLoad()

    def visit_AugStore(self, node):
        return dual_ast.AugStore()

    def visit_Del(self, node):
        return dual_ast.Del()

    def visit_Load(self, node):
        return dual_ast.Load()

    def visit_Param(self, node):
        return dual_ast.Param()

    def visit_Store(self, node):
        return dual_ast.Store()

    def visit_BoolOp(self, node):
        classname = node.op.__class__.__name__
        if isinstance(node.op, (ast.And, ast.Or)):
            op = getattr(dual_ast, classname)()
        else:
            self.log_error(
                "Unknown boolean operator: {0}".format(classname), node
            )
            return None

        values = list(map(self.visit, node.values))
        return dual_ast.BoolOp(op=op, values=values)

    def visit_BinOp(self, node):
        classname = node.op.__class__.__name__
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
            op = getattr(dual_ast, classname)()
        else:
            self.log_error("Unknown operator: {0}".format(classname), node)
            return None

        left = self.visit(node.left)
        right = self.visit(node.right)
        return dual_ast.BinOp(left=left, op=op, right=right)

    def visit_UnaryOp(self, node):
        classname = node.op.__class__.__name__
        if isinstance(node.op, (ast.UAdd, ast.USub, ast.Invert, ast.Not)):
            op = getattr(dual_ast, classname)()
        else:
            self.log_error("Unknown operator: {0}".format(classname))
            return
        operand = self.visit(node.operand)

        return dual_ast.UnaryOp(op=op, operand=operand)

    def visit_IfExp(self, node):
        return dual_ast.IfExp(
            test=self.visit(node.test),
            body=self.visit(node.body),
            orelse=self.visit(node.orelse)
        )
