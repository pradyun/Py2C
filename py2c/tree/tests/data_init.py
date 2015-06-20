"""Data for unit-tests for `py2c.tree`
"""

from py2c import tree


# =============================================================================
# Helper classes
# =============================================================================
class NodeWithoutFieldsAttribute(tree.Node):
    """A base node that doesn't define the fields attribute
    """


class EmptyNode(tree.Node):
    """An empty node with no fields
    """
    _fields = []


class BasicNode(tree.Node):
    """Basic node
    """
    _fields = [
        ('f1', int, "NEEDED"),
    ]


class InheritingNodeWithoutFieldsAttributeNode(BasicNode):
    """A node that inherits from BasicNode but doesn't declare fields.

    (It should inherit the fields from parent)
    """


class BasicNodeCopy(tree.Node):
    """Equivalent but not equal to BasicNode
    """
    _fields = [
        ('f1', int, "NEEDED"),
    ]


class AllIntModifiersNode(tree.Node):
    """Node with all modifiers
    """
    _fields = [
        ('f1', int, "NEEDED"),
        ('f2', int, "OPTIONAL"),
        ('f3', int, "ZERO_OR_MORE"),
        ('f4', int, "ONE_OR_MORE"),
    ]


class NodeWithANodeField(tree.Node):
    """Node with another node as child
    """
    _fields = [
        ('child', BasicNode, "NEEDED"),
    ]


class InvalidModifierNode(tree.Node):
    """Node with invalid modifier
    """
    _fields = [
        ('f1', int, None),
    ]


# -----------------------------------------------------------------------------


class SubClass(tree.identifier):
    """A subclass of identifier.

    Used for checking identifier's behaviour with subclasses.
    """


# =============================================================================
# Test Cases
# =============================================================================
Node_initialization_valid_cases = [
    (
        "zero fields; without any arguments",
        EmptyNode, [], {}, {}
    ),
    (
        "one NEEDED field; without any arguments",
        BasicNode, [], {}, {}
    ),
    (
        "one NEEDED field; with 1 valid positional argument",
        BasicNode, [1], {}, {"f1": 1}
    ),
    (
        "one NEEDED field; with 1 valid keyword argument",
        BasicNode, [], {"f1": 1}, {"f1": 1}
    ),
    (
        "all types of fields; with minimal valid positional arguments",
        AllIntModifiersNode, [1, None, (), (2,)], {}, {
            "f1": 1, "f2": None, "f3": (), "f4": (2,)
        }
    ),
    (
        "all types of fields; with valid positional arguments",
        AllIntModifiersNode, [1, 2, (3, 4, 5), (6, 7, 8)], {}, {
            "f1": 1, "f2": 2, "f3": (3, 4, 5), "f4": (6, 7, 8),
        }
    ),
    (
        "one inherited NEEDED field; without any arguments",
        InheritingNodeWithoutFieldsAttributeNode, [], {}, {}
    ),
    (
        "one inherited NEEDED field; with 1 valid positional argument",
        InheritingNodeWithoutFieldsAttributeNode, [1], {}, {"f1": 1}
    ),
    (
        "one inherited NEEDED field; with 1 valid keyword argument",
        InheritingNodeWithoutFieldsAttributeNode, [], {"f1": 1}, {"f1": 1}
    ),
]

Node_initialization_invalid_cases = [
    (
        "no fields attribute defined",
        NodeWithoutFieldsAttribute, [], {},
        tree.InvalidInitializationError,
        ["iterable", "_fields"]
    ),
    (
        "zero fields with some argument",
        EmptyNode, [1], {},
        tree.InvalidInitializationError,
        ["no", "arguments"]
    ),
    (
        "one field with extra arguments",
        BasicNode, [1, 2], {},
        tree.InvalidInitializationError,
        ["0 or 1", "argument", "!arguments"]
    ),
    (
        "modifiers with incorrect number of arguments",
        AllIntModifiersNode, [1], {},
        tree.InvalidInitializationError,
        ["0 or 4", "arguments"]
    ),
    (
        "missing arguments",
        AllIntModifiersNode, [1], {},
        tree.InvalidInitializationError,
        ["AllIntModifiersNode", "0 or 4", "arguments"]
    ),
    (
        "a child with missing arguments",
        lambda: NodeWithANodeField(AllIntModifiersNode(1)), [], {},
        tree.InvalidInitializationError,
        ["AllIntModifiersNode", "0 or 4", "arguments"]
    ),
    (
        "an invalid/unknown modifier",
        InvalidModifierNode, [], {},
        tree.InvalidInitializationError,
        ["InvalidModifierNode", "f1", "invalid modifier"]
    ),
]

Node_assignment_valid_cases = [
    (
        "NEEDED with False-ish value",
        AllIntModifiersNode, "f1", 0
    ),
    (
        "NEEDED with True-ish value",
        AllIntModifiersNode, "f1", 1
    ),
    (
        "OPTIONAL with False-ish value",
        AllIntModifiersNode, "f2", 0
    ),
    (
        "OPTIONAL with True-ish value",
        AllIntModifiersNode, "f2", 1
    ),
    (
        "OPTIONAL with None",
        AllIntModifiersNode, "f2", None
    ),
    (
        "ZERO_OR_MORE with an empty tuple",
        AllIntModifiersNode, "f3", ()
    ),
    (
        "ZERO_OR_MORE with a tuple with one element",
        AllIntModifiersNode, "f3", (1,)
    ),
    (
        "ZERO_OR_MORE with a tuple with four element",
        AllIntModifiersNode, "f3", (1, 2, 3, 4)
    ),
    (
        "ZERO_OR_MORE with an empty list",
        AllIntModifiersNode, "f3", []
    ),
    (
        "ZERO_OR_MORE with a list with one element",
        AllIntModifiersNode, "f3", [1]
    ),
    (
        "ZERO_OR_MORE with a list with four element",
        AllIntModifiersNode, "f3", [1, 2, 3, 4]
    ),
    (
        "ONE_OR_MORE with a tuple with one element",
        AllIntModifiersNode, "f4", (1,)
    ),
    (
        "ONE_OR_MORE with a tuple with four element",
        AllIntModifiersNode, "f4", (1, 2, 3, 4)
    ),
    (
        "ONE_OR_MORE with a list with one element",
        AllIntModifiersNode, "f4", [1]
    ),
    (
        "ONE_OR_MORE with a list with four element",
        AllIntModifiersNode, "f4", [1, 2, 3, 4]
    ),
]

Node_assignment_invalid_cases = [
    (
        "non existent field",
        BasicNode, "bar", 1,
        tree.FieldError, ["bar", "no field"]
    ),
    (
        "NEEDED with incorrect type",
        AllIntModifiersNode, "f1", "",
        tree.WrongTypeError
    ),
    (
        "OPTIONAL with incorrect type",
        AllIntModifiersNode, "f2", "",
        tree.WrongTypeError
    ),
    (
        "ZERO_OR_MORE with incorrect type",
        AllIntModifiersNode, "f3", "",
        tree.WrongTypeError
    ),
    (
        "ZERO_OR_MORE with tuple containing incorrect type",
        AllIntModifiersNode, "f3", ("",),
        tree.WrongTypeError
    ),
    (
        "ZERO_OR_MORE with list containing incorrect type",
        AllIntModifiersNode, "f3", [""],
        tree.WrongTypeError
    ),
    (
        "ONE_OR_MORE with incorrect type",
        AllIntModifiersNode, "f4", "",
        tree.WrongTypeError
    ),
    (
        "ONE_OR_MORE with empty tuple",
        AllIntModifiersNode, "f4", (),
        tree.WrongTypeError
    ),
    (
        "ONE_OR_MORE with empty list",
        AllIntModifiersNode, "f4", [],
        tree.WrongTypeError
    ),
    (
        "ONE_OR_MORE with tuple containing incorrect type",
        AllIntModifiersNode, "f4", ("",),
        tree.WrongTypeError
    ),
    (
        "ONE_OR_MORE with list containing incorrect type",
        AllIntModifiersNode, "f4", [""],
        tree.WrongTypeError
    ),
]

Node_finalization_valid_cases = [
    (
        "valid attributes",
        AllIntModifiersNode(1, 2, [], [3]),
        {"f1": 1, "f2": 2, "f3": (), "f4": (3,)}
    ),
    (
        "valid attributes (optionals not given)",
        AllIntModifiersNode(f1=1, f4=[2]),
        {"f1": 1, "f2": None, "f3": (), "f4": (2,)}
    ),
]

Node_finalization_invalid_cases = [
    (
        "no parameters",
        AllIntModifiersNode(),
        ["missing", "f1", "f4", "!f2", "!f3"]
    ),
    (
        "a child without parameters",
        NodeWithANodeField(BasicNode()),
        ["missing", "f1"]
    )
]

Node_equality_equal_cases = [
    (
        "same class nodes with equal attributes",
        BasicNode(1), BasicNode(1)
    ),
    (
        "same class nodes with same class children "
        "with equal attributes",
        NodeWithANodeField(BasicNode(1)),
        NodeWithANodeField(BasicNode(1))
    ),
]

Node_equality_not_equal_cases = [
    (
        "same class nodes with non-equal attributes",
        BasicNode(0), BasicNode(1)
    ),
    (
        "same class nodes with same class children with non-equal "
        "attributes",
        NodeWithANodeField(BasicNode(0)),
        NodeWithANodeField(BasicNode(1))
    ),
    (
        "different class nodes with same attributes",
        BasicNode(1), BasicNodeCopy(1)
    ),
]

Node_repr_cases = [
    (
        "no-field node",
        BasicNode(), "BasicNode()"
    ),
    (
        "no-field node with a different name",
        BasicNodeCopy(), "BasicNodeCopy()"
    ),
    (
        "multi-field node with no arguments",
        AllIntModifiersNode(), "AllIntModifiersNode()"
    ),
    (
        "node with Node fields but no arguments",
        NodeWithANodeField(), "NodeWithANodeField()"
    ),
    (
        "multi-field node with minimal number of arguments",
        AllIntModifiersNode(f1=1, f2=None),
        "AllIntModifiersNode(f1=1, f2=None)"
    ),
    (
        "multi-field node with optional arguments provided",
        AllIntModifiersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6)),
        "AllIntModifiersNode(f1=1, f2=None, f3=[3], f4=(4, 5, 6))"
    )
]

# -----------------------------------------------------------------------------

identifier_valid_cases = [
    ("a valid string", "valid_name"),
    ("a really long string", "really" * 100 + "_long_name"),
    ("a single character string", "c"),
    ("a snake_case string", "valid_name"),
    ("a CamelCase string", "ValidName"),
    ("a LOUD_CASE string", "VALID_NAME"),
    ("a valid string with numbers and underscore", "Valid_1_name"),
    ("a string with leading and trailing underscores", "_valid_name_"),
    # Might never be used but support is **very** important! :P
    ("a string containing a unicode character", "虎"),
]

identifier_invalid_cases = [
    ("an empty string", ""),
    ("a string containing spaces", "invalid name"),
    ("a string containing hyphen", "invalid-name"),
    ("a string containing full-stop/dot", "invalid.name"),
]

identifier_is_subclass_cases = [
    ("str", str),
    ("an inheriting sub-class", SubClass),
]

identifier_not_is_subclass_cases = [
    ("object", object),
    ("float", float),
    ("int", int),
]
