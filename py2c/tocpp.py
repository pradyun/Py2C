#A node visitor that spews C++ when told to visit a node
#This includes every node defined in /py2c/syntax_tree/python.py
#But at present only works if all nodes in the tree return
#something other than self.generic_visit(node) (only aritmetic expressions)
import ast
from syntax_tree import python
from textwrap import indent
from functions import functions

class tocpp(ast.NodeVisitor):
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.imports = set() #all files imported
        self.context = [] #append current node before entering children unless they definitely don't need it
    def visit_PyAST(self, node): return self.generic_visit(node)
    def visit_mod(self, node): return self.generic_visit(node)
    def visit_stmt(self, node): return self.generic_visit(node)
    def visit_expr(self, node): return self.generic_visit(node)
    def visit_expr_context(self, node): return self.generic_visit(node)
    def visit_slice(self, node): return self.generic_visit(node)
    def visit_boolop(self, node): return self.generic_visit(node)
    def visit_operator(self, node): return self.generic_visit(node)
    def visit_unaryop(self, node): return self.generic_visit(node)
    def visit_cmpop(self, node): return self.generic_visit(node)
    def visit_arg(self, node): return self.generic_visit(node)
    def visit_comprehension(self, node): return self.generic_visit(node)
    def visit_arguments(self, node): return self.generic_visit(node)
    def visit_keyword(self, node): return self.generic_visit(node)
    def visit_alias(self, node): return self.generic_visit(node)
    def visit_withitem(self, node): return self.generic_visit(node)
    def visit_ExceptHandler(self, node): return self.generic_visit(node)
    def visit_Module(self, node):
        program = list()
        for n in node.body:
            program.append(self.visit(n))
        imports = list()
        for n in list(self.imports):
            imports.append('#include "%s"' % n)
        return '\n'.join(imports) + '\n' + '\n'.join(program)
    def visit_FunctionDef(self, node): return self.generic_visit(node)
    def visit_ClassDef(self, node): return self.generic_visit(node)
    def visit_Return(self, node):
        return 'return %s;' % self.visit(node.value)
    def visit_Delete(self, node): return self.generic_visit(node)
    def visit_Assign(self, node): return self.generic_visit(node)
    def visit_AugAssign(self, node): return self.generic_visit(node)
    def visit_For(self, node): return self.generic_visit(node)
    def visit_While(self, node): return self.generic_visit(node)
    def visit_If(self, node):
        ts = self.visit(node.test)
        ys = []
        for n in node.body:
            ys.append(self.visit(n))
        yes = '    ' + '\n    '.join(ys)
        no = []
        for n in node.orelse:
            no.append(self.visit(n))
        if no:
            n = '    ' + '\n    '.join(no)
            return 'if (%s) {\n%s\n}\nelse {\n%s\n}\n' % (ts, yes, n)
        else:
            return 'if (%s) {\n%s\n}\n' % (ts, yes)
    def visit_With(self, node): return self.generic_visit(node)
    def visit_Raise(self, node): return self.generic_visit(node)
    def visit_Try(self, node): return self.generic_visit(node)
    def visit_Assert(self, node): return self.generic_visit(node)
    def visit_Import(self, node): return self.generic_visit(node)
    def visit_ImportFrom(self, node): return self.generic_visit(node)
    def visit_Future(self, node): return self.generic_visit(node)
    def visit_Global(self, node): return self.generic_visit(node)
    def visit_Nonlocal(self, node): return self.generic_visit(node)
    def visit_Expr(self, node):
        return '(' + self.visit(node.value) + ');'
    def visit_Pass(self, node):
        return '0;' #I think this will work...
    def visit_Break(self, node): return self.generic_visit(node)
    def visit_Continue(self, node): return self.generic_visit(node)
    def visit_BoolOp(self, node):
        v = []
        for n in node.values:
            v.append(self.visit(n))
        return '(' + self.visit(node.op).join(v) + ')'
    def visit_BinOp(self, node):
        l = self.visit(node.left)
        r = self.visit(node.right)
        if node.op.__class__ == python.FloorDiv:
            return '((%s - (%s %% %s)) / %s)' % (l, l, r, r)
        elif node.op.__class__ == python.Pow:
            return 'pow(%s, %s)' % (l, r)
            #import C++ file containing equivalents of all builtin functions
        else:
            return '(%s %s %s)' % (l, self.visit(node.op), r)
    def visit_UnaryOp(self, node):
        return self.visit(node.op) + ' ' + self.visit(node.operand)
    def visit_Lambda(self, node): return self.generic_visit(node)
    def visit_IfExp(self, node): return self.generic_visit(node)
    def visit_Dict(self, node): return self.generic_visit(node)
    def visit_Set(self, node): return self.generic_visit(node)
    def visit_ListComp(self, node): return self.generic_visit(node)
    def visit_SetComp(self, node): return self.generic_visit(node)
    def visit_DictComp(self, node): return self.generic_visit(node)
    def visit_GeneratorExp(self, node): return self.generic_visit(node)
    def visit_Yield(self, node): return self.generic_visit(node)
    def visit_YieldFrom(self, node): return self.generic_visit(node)
    def visit_Compare(self, node):
        lst = list(zip(node.ops, node.comparators))
        ret = ''
        for r in lst:
            ret += ' ' + self.visit(r[0]) + ' ' + self.visit(r[1])
        return '(' + self.visit(node.left) + ret + ')'
    def visit_Call(self, node): #needs work, but will suffice for simple things...
        if node.func in functions:
            self.imports.add(functions[node.func][1])
            return functions[node.func][0].format(*self.generic_visit[node.args])
        else:
            return '%s(%s)' % (node.func, ', '.join(self.generic_visit[node.args]))
    def visit_Attribute(self, node): return self.generic_visit(node)
    def visit_Subscript(self, node): return self.generic_visit(node)
    def visit_Starred(self, node): return self.generic_visit(node)
    def visit_Name(self, node):
        if node.ctx.__class__ == python.Load:
            return node.id
        elif node.ctx.__class__ == python.Del:
            return 'Del not implemented yet...'
        else:
            return 'Store not implemented yet...'
    def visit_List(self, node): return self.generic_visit(node)
    def visit_Tuple(self, node): return self.generic_visit(node)
    def visit_Ellipsis(self, node): return self.generic_visit(node)
    def visit_NameConstant(self, node): return self.generic_visit(node)
    def visit_literal(self, node): return self.generic_visit(node)
    def visit_Str(self, node):
        return node.s
    def visit_Bytes(self, node): return self.generic_visit(node)
    def visit_Bool(self, node): return self.generic_visit(node)
    def visit_num(self, node): return self.generic_visit(node)
    def visit_Int(self, node):
        return str(node.n)
    def visit_Float(self, node): return self.generic_visit(node)
    def visit_Complex(self, node): return self.generic_visit(node)
    def visit_Load(self, node): return self.generic_visit(node)
    def visit_Store(self, node): return self.generic_visit(node)
    def visit_Del(self, node): return self.generic_visit(node)
    def visit_AugLoad(self, node): return self.generic_visit(node)
    def visit_AugStore(self, node): return self.generic_visit(node)
    def visit_Param(self, node): return self.generic_visit(node)
    def visit_Slice(self, node): return self.generic_visit(node)
    def visit_ExtSlice(self, node): return self.generic_visit(node)
    def visit_Index(self, node): return self.generic_visit(node)
    def visit_And(self, node):
        return 'and'
    def visit_Or(self, node):
        return 'or'
    def visit_Add(self, node):
        return '+'
    def visit_Sub(self, node):
        return '-'
    def visit_Mult(self, node):
        return '*'
    def visit_Div(self, node):
        return '/'
    def visit_Mod(self, node):
        return '%'
    def visit_Pow(self, node): return self.generic_visit(node)
    def visit_LShift(self, node):
        return '<<'
    def visit_RShift(self, node):
        return '>>'
    def visit_BitOr(self, node):
        return '|'
    def visit_BitXor(self, node):
        return '^'
    def visit_BitAnd(self, node):
        return '&'
    def visit_FloorDiv(self, node): return self.generic_visit(node)
    def visit_Invert(self, node):
        return '~'
    def visit_Not(self, node):
        return '!'
    def visit_UAdd(self, node):
        return '+'
    def visit_USub(self, node):
        return '-'
    def visit_Eq(self, node):
        return '=='
    def visit_NotEq(self, node):
        return '!='
    def visit_Lt(self, node):
        return '<'
    def visit_LtE(self, node):
        return '<='
    def visit_Gt(self, node):
        return '>'
    def visit_GtE(self, node):
        return '>='
    def visit_Is(self, node): return self.generic_visit(node)
    def visit_IsNot(self, node): return self.generic_visit(node)
    def visit_In(self, node): return self.generic_visit(node)
    def visit_NotIn(self, node): return self.generic_visit(node)
    
if __name__ == '__main__':
    import translator
    con = translator.Python2ASTTranslator().get_node
    nv = tocpp()
    for s in ['1+2', '1*2', '8**7', '3/4', '3//4', '- 3', 'not 5']:
        print(s, '    ', eval(s), '    ', nv.visit(con(s).body[0].value))
    print()
    print(nv.visit(con('1+2+(3*4)+5+6\n4//7 + 3')))
    print()
    print(nv.visit(con('if 3: 4*3')))
    print(nv.visit(con('if 1==2: 5/9 - 6')))
