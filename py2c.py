#!/usr/bin/env python

import ast
import c_ast
c_ast.prepare()

class ASTTranslator(ast.NodeVisitor):
    """Translates Python code into C code
    This is a NodeVisitor that visits the Python AST validates it for conversion
    and creates another AST, for C code (with type definitions and other stuff),
    from which C code is generated.
    """
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

    def body(self, li):
        return map(self.visit, li)

    def visit_Module(self, node):
        li = self.body(node.body)
        return c_ast.Module(li)

    def visit_Num(self, node):
        if isinstance(node.n, int):
            return c_ast.Int(n=node.n)
        elif isinstance(node.n, float):
            return c_ast.Float(n=node.n)
        else:
            msg = "Only ints and floats supported, {0} numbers not supported"
            raise ValueError(msg.format(node.n.__class__.__name__))

def main():
    text = "2"
    node = ast.parse(text)
    print ast.dump(node)
    t = ASTTranslator()
    print t.visit(node)

def get_C_AST(py_ast):
    """Translate Python AST in C AST"""
    translator = ASTTranslator()
    try:
        return translator.visit(py_ast)
    except Exception as e:
        print vars(e)


if __name__ == '__main__':
    main()
