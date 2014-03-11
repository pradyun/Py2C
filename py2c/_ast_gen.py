#! /usr/bin/env python
"""AST nodes file generator

This file generates the ast that we use as the meduim to translate Python code.
It makes it possible to translate Python code to C code without multiple AST
systems.
"""
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
import os
import re
from textwrap import dedent

import ply.lex
import ply.yacc

_PREFIX = dedent("""
""").strip()


#-------------------------------------------------------------------------------
# Exceptions
#-------------------------------------------------------------------------------
class ParserError(Exception):
    """Errors raised by the Parser while Parsing
    """


#-------------------------------------------------------------------------------
# Helper Class
#-------------------------------------------------------------------------------
class Node(object):
    """Represents a definition in the AST definitions
    """
    def __init__(self, name, parent=None, attrs=None):
        super(Node, self).__init__()
        self.name = name
        self.parent = parent
        self.attrs = attrs
        self._verify()

    def _verify(self):
        seen = []
        duplicated = []
        for name, type_, modifier in self.attrs:
            if name in seen:
                duplicated.append(name)
            else:
                seen.append(name)

        if duplicated:
            msg = "Multiple declarations in {!r} of attribute{} {!r}".format(
                self.name,
                "s" if len(duplicated) > 1 else "",
                ", ".join(duplicated)
            )
            raise ParserError(msg)

    def __repr__(self):
        return "Node({!r}, {!r}, {!r})".format(
            self.name, self.parent, self.attrs
        )

    def __eq__(self, other):
        return (
            hasattr(other, "name") and self.name == other.name and
            hasattr(other, "parent") and self.parent == other.parent and
            hasattr(other, "attrs") and self.attrs == other.attrs
        )


#-------------------------------------------------------------------------------
# Parsing of AST nodes declaration
#-------------------------------------------------------------------------------
class Parser(object):
    """Parses the definitions in the definition files
    """
    def __init__(self):
        super(Parser, self).__init__()
        self.tokens = ("NAME",)
        self.literals = "()[]:*?+,"

        # Tokens for lexer
        self.t_NAME = "\w+"
        self.t_ignore = "\n \t"

        self._lexer = ply.lex.lex(module=self)
        self._parser = ply.yacc.yacc(module=self, start="start")

    def remove_comments(self, text):
        return re.sub(r"(?m)\#.*($|\n)", "", text)

    def parse(self, text):
        """Parses the definition text into a data representaton of it.
        """
        text = self.remove_comments(text)
        return self._parser.parse(text, lexer=self._lexer)

    def t_newline(self, t):
        r"\n"
        t.lexer.lineno += 1

    def p_error(self, t):
        raise ParserError("while Parsing: " + str(t))

    def t_error(self, t):
        raise ParserError("while Tokenizing: " + str(t))

    #---------------------------------------------------------------------------
    # Parsing
    #---------------------------------------------------------------------------
    def p_empty(self, p):
        "empty : "

    def p_start(self, p):
        "start : zero_or_more_declaration"
        p[0] = p[1]

    def p_zero_or_more_declaration(self, p):
        """zero_or_more_declaration : zero_or_more_declaration declaration
                                    | empty
        """
        if len(p) == 2:
            p[0] = ()
        else:
            p[0] = p[1] + (p[2],)

    def p_declaration(self, p):
        "declaration : NAME parent_class_opt ':' '[' attr_list ']'"
        p[0] = Node(p[1], p[2], p[5])

    def p_parent_class_opt(self, p):
        """parent_class_opt : '(' NAME ')'
                            | empty
        """
        if len(p) > 2:
            p[0] = p[2]
        else:
            p[0] = None

    def p_attr_list_1(self, p):
        """attr_list : attr more_attrs_maybe ','
                     | attr more_attrs_maybe
                     | empty
        """
        if len(p) > 2:
            p[0] = [p[1]] + p[2]
        else:
            p[0] = []

    def p_more_attrs_maybe(self, p):
        """more_attrs_maybe : more_attrs_maybe ',' attr
                            | empty
        """
        if len(p) > 2:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = []

    def p_attr(self, p):
        "attr : NAME modifier NAME"
        p[0] = (p[3], p[1], p[2])

    def p_modifier(self, p):
        """modifier : empty
                    | '?'
                    | '+'
                    | '*'
        """
        if p[1] == "+":
            p[0] = "ONE_OR_MORE"
        elif p[1] == "*":
            p[0] = "ZERO_OR_MORE"
        elif p[1] == "?":
            p[0] = "OPTIONAL"
        else:
            p[0] = "NEEDED"


#-------------------------------------------------------------------------------
# Generation of sources for AST nodes class
#-------------------------------------------------------------------------------
class SourceGenerator(object):
    """Generates the code from the Parser's parsed data
    """
    def __init__(self):
        super(SourceGenerator, self).__init__()

    def generate_sources(self, data):
        """Generates source code from the data generated by :py:class:`Parser`
        """
        classes = []
        for node in data:
            classes.append(self._translate_node(node))
        return "\n\n\n".join(classes)

    def _translate_node(self, node):
        name = node.name

        if node.parent is None:
            parent = "object"
            field_text = self._prettify_list(node.attrs)
        else:
            parent = node.parent
            field_text = parent + "._fields"
            if node.attrs:
                field_text += " + " + self._prettify_list(node.attrs)

        return dedent("""
            class {0}({1}):
                _fields = {2}
        """).strip().format(name, parent, field_text)

    def _prettify_list(self, li):
        if li == []:
            return "[]"
        else:
            lines = ["["]
            for elem in li:
                lines.append((" "*8 + "({!r}, {}, {}),".format(*elem)))
            lines.append(" "*4 + "]")

            return "\n".join(lines)


# API for dual_ast
def generate(base_dir, files_to_convert):
    content = []
    for fname in files_to_convert:
        with open(os.path.join(base_dir, fname)) as f:
            content.append(f.read())

    text = "\n\n".join(content)

    parser = Parser()
    src_gen = SourceGenerator()

    return src_gen.generate_sources(parser.parse(text))


if __name__ == '__main__':
    print(generate("", ["python.ast"]))
