#!/usr/bin/env python

from __future__ import print_function
import ast
import inspect
import c_ast
c_ast.prepare()


__all__ = ["ASTTranslator", "c_ast"]


class ASTTranslator(ast.NodeVisitor):
    """Translates Python AST into C AST

    This is a NodeVisitor that visits the Python AST validates it for conversion
    and creates another AST, for C code (with type definitions and other stuff),
    from which C code is generated.

    Attributes:
        errors: A list that contains the error-messages that of errors that
                occurred during translation.
    """
    def __init__(self):
        super(ASTTranslator, self).__init__()
        self.setup()

    def setup(self):
        self.errors = []

    # Errors
    def log_error(self, msg, node=None):
        import pprint
        stack = inspect.stack()
        if len(stack) > 1:
            caller = stack[1][3]
            # remove 'visit_'
            if caller.startswith('visit_'):
                caller = caller[6:]
        else:
            caller = None

        if caller is not None:
            msg = "(Node type: {0}) {1}".format(caller, msg)
        if hasattr(node, "lineno"):
            msg += "Check Line ({0}): {1}".format(node.lineno, msg)
        self.errors.append(msg)

    def print_errors(self):
        if not self.errors:
            return

        print("Error(s) occurred while translating Python AST into C ast")
        for msg in self.errors:
            print(c_ast.indent(msg, ' - '))

    def get_node(self, node):
        """Get the C AST from the Python AST `node`
        Args:
            node: The Python AST to be converted to C AST
        Returns:
            A C node, from the c_ast.py
        Raises:
            Exception: If the AST could not be converted, due to some error
                       Raised after printing those errors.
        """
        self.setup()
        retval = self.visit(node)
        if self.errors:
            self.print_errors()
            return None
        else:
            return retval

    # Modified to return values
    def generic_visit(self, node):
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
        return map(self.visit, body)

    def visit_Module(self, node):
        return c_ast.Module(self.body(node.body))

    def visit_Print(self, node, py3=False):
        if py3: # python 3 print function
            keywords = {}
            if node.keywords is not None:
                for kw in node.keywords:
                    keywords[kw.arg] = kw.value

            sep = keywords.get('sep', ast.Str(' ')).s
            end = keywords.get('end', ast.Str('\n')).s
            dest = keywords.get('file', None)
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

        return c_ast.Print(dest=dest, values=values, sep=sep, end=end)

    def visit_Call(self, node):
        if node.func.id == 'print': # Python 3 print
            return self.visit_Print(node, True)

        if node.keywords:
            self.log_error("Calls with keyword arguments not supported", node)
        if node.starargs is not None or node.kwargs is not None:
            self.log_error("Calls with starred arguments not supported", node)
        func = self.visit(node.func)
        args = map(self.visit, node.args)
        return c_ast.Call(func=func, args=args)

    def visit_Num(self, node):
        if isinstance(node.n, int):
            return c_ast.Int(n=node.n)
        elif isinstance(node.n, float):
            return c_ast.Float(n=node.n)
        else:
            msg = "Only ints and floats supported, {0} numbers not supported"
            raise ValueError(msg.format(node.n.__class__.__name__))

    def visit_Name(self, node):
        return c_ast.Name(id=node.id)

    def visit_Str(self, node):
        return c_ast.Str(s=node.s)

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            op = c_ast.And()
        elif isinstance(node.op, ast.Or):
            op = c_ast.Or()
        values = map(self.visit, node.values)
        return c_ast.BoolOp(op=op, values=values)

    def visit_BinOp(self, node):
        classname = node.op.__class__.__name__
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod)):
            op = getattr(c_ast, classname)()
        else:
            self.log_error("Unknown operator: {0}".format(classname), node)
            return None

        left = self.visit(node.left)
        right = self.visit(node.right)
        return c_ast.BinOp(left=left, op=op, right=right)

    def visit_UnaryOp(self, node):
        classname = node.op.__class__.__name__
        if isinstance(node.op, (ast.And, ast.Not)):
            op = getattr(c_ast, classname)()
        else:
            raise Exception("Unknown operator: {0}".format(classname))
        operand = self.visit(node.operand)

        return c_ast.UnaryOp(op=op, operand=operand)

    def visit_IfExp(self, node):
        return c_ast.IfExp(test=self.visit(node.test),
                           body=self.visit(node.body),
                           orelse=self.visit(node.orelse))



if __name__ == '__main__':  # For the current development stuff
    # text = 'foo if bar else baz'
    # node = ast.parse(text)
    node = ast.BinOp(op='Blah', left=ast.Name(id="foo"), right=ast.Name(id="bar"))
    print(ast.dump(node))
    t = ASTTranslator()
    print(t.get_node(node))


