"""Implements the base class for all CodeGenerators in `py2c.code_generators`
"""
import abc
import inspect
from . import dual_ast
from .utils import add_metaclass


class CodeGenerationError(Exception):
    """Base class for errors raised during CodeGeneration
    """
    def __init__(self, errors):
        super(CodeGenerationError, self).__init__()
        self.errors = errors


@add_metaclass(abc.ABCMeta)
class AbstractCodeGenerator(object):
    """ABC for all CodeGenerators
    """
    def __init__(self):
        super(AbstractCodeGenerator, self).__init__()
        self.reset()

    #---------------------------------------------------------------------------
    # API
    #---------------------------------------------------------------------------
    # Errors
    def reset(self):
        self.errors = []

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
            caller_name = None

        if caller_name is not None:
            msg = "(Node type: {0}) {1}".format(caller_name, msg)

        if hasattr(node, "lineno"):
            msg += "Check Line ({0}): {1}".format(node.lineno, msg)
        self.errors.append(msg)

    def handle_errors(self):
        if not self.errors:
            return
        raise CodeGenerationError()

    # Providing output
    def get_code(self, node):
        """Get code from dual AST node: `node`

        Args:
            node: The AST to be converted to code
        Returns:
            A string containing the code
        Raises:
            CodeGenerationError when there is any error during CodeGeneration
        """
        self.reset()
        retval = self.visit(node)
        self.handle_errors()
        return retval

    #---------------------------------------------------------------------------
    # Code Generation API, like ast.NodeVisitor
    #---------------------------------------------------------------------------
    def visit(self, node):
        """Visit a node.
        """
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    @abc.abstractmethod
    def generic_visit(self, node):
        """Called if no explicit visitor function exists for a node.
        """
        for field, value in dual_ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dual_ast.AST):
                        self.visit(item)
            elif isinstance(value, dual_ast.AST):
                self.visit(value)
