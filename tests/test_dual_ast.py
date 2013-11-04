#!/usr/bin/env python

import unittest

import py2c.dual_ast as dual_ast


class DummyNode(dual_ast.AST):
    def __init__(self, attrs=None, *args, **kwargs):
        if attrs is None:
            attrs = []
        self._attrs = attrs
        super(DummyNode, self).__init__(*args, **kwargs)


# -----------------------------------
class ASTTestCase(unittest.TestCase):
    """Tests for AST node"""

    def test_init1(self):
        "A no-subclass directly invocation of init method of AST"
        with self.assertRaises(AttributeError):
            dual_ast.AST()

    def test_equality_equal1(self):
        "Test for equality for really equal Nodes"
        attrs = [("foo", None, False), ('bar', '[]', True)]

        node1 = DummyNode(attrs)
        node2 = DummyNode(attrs)

        self.assertEqual(node1, node2)

    def test_equality_equal2(self):
        "Test for equality with node when it has children nodes"
        node1 = DummyNode(dest=DummyNode(id='foo'), values=[],
                          sep=' ', end='\n')
        node2 = DummyNode(dest=DummyNode(id='foo'), values=[],
                          sep=' ', end='\n')
        self.assertEqual(node1, node2)

    def test_equality_with_extra_attrs(self):
        "Test for (in)equality on nodes with in-equal attributes"
        node1 = DummyNode([("foo", None, False)])
        node2 = DummyNode([("foo", None, False), ("bar", None, False)])

        self.assertNotEqual(node1, node2)

    def test_equality_diff_type(self):
        "Test for inequality on the basis of type"
        node1 = DummyNode([])

        self.assertNotEqual(node1, "I'm not equal to a Node")

    # A really important and useful test. Create the node_names list!!
    def test_nodes_exist(self):
        "Checks if to see that all required nodes exist in '_dual_ast.py'"

        node_names = [
            # The all important node
            "AST",
            ## Base nodes
            "boolop", "cmpop", "expr", "expr_context", "mod", "operator",
            "slice", "stmt", "unaryop",
            ## Common Nodes
            "BinOp", "BoolOp", "Break", "Expression", "If", "Interactive",
            "Module", "Return", "Str", "Suite", "UnaryOp", "While",
            ## Python nodes
            "Add", "And", "Assert", "Assign", "Attribute", "AugAssign",
            "AugLoad", "AugStore", "BitAnd", "BitOr", "BitXor", "Bytes", "Call",
            "ClassDef", "Compare", "Continue", "Del", "Delete", "Dict",
            "DictComp", "Div", "Ellipsis", "Eq", "ExceptHandler", "Exec",
            "Expr", "Expression", "ExtSlice", "FloorDiv", "FunctionDef",
            "GeneratorExp", "Global", "Gt", "GtE", "IfExp", "Import",
            "ImportFrom", "In", "Index", "Invert", "Is", "IsNot", "LShift",
            "Lambda", "List", "ListComp", "Load", "Lt", "LtE", "Mod","Mult",
            "Name", "Nonlocal", "Not", "NotEq", "NotIn", "Num", "Or", "Param",
            "Pass", "Pow", "Print", "Py_For", "RShift", "Raise", "Repr", "Set",
            "SetComp", "Slice", "Starred", "Store", "Sub", "Subscript", "Try",
            "TryExcept", "TryFinally", "Tuple", "UAdd", "USub", "With", "Yield",
            "YieldFrom",
            # Helper Nodes
            "alias", "arg", "arguments", "comprehension","excepthandler",
            "keyword", "withitem",
            ## C nodes
            "Block", "C_For", "Case", "Char", "Decl", "Default", "DoWhile",
            "EnumDecl", "EnumItem", "Float", "Goto", "Int", "Label", "Switch",
        ]

        missing = []
        for name in node_names:
            if not hasattr(dual_ast, name):
                missing.append(name)

        extra = []
        for name in dir(dual_ast):
            if name not in node_names and not name.startswith("_"):
                extra.append(name)

        if not (missing or extra):
            return

        # If we are here, we have failed the test
        msg = ["dual_ast has "]
        write = msg.append

        if missing and extra:
            write("missing and extra")
        elif missing:
            write("missing")
        elif extra:
            write("extra")

        write(" attributes")

        if missing:
            write("\nMissing: ")
            write(", ".join(missing))
        if extra:
            write("\nExtra: ")
            write(", ".join(extra))

        self.fail("".join(msg))


if __name__ == '__main__':
    unittest.main()
