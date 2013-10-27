"""
Contains the compatibility related stuff to allow for compatibility across\
Python versions"""
import sys

# Compatibility across versions
PY3K = sys.version_info[0] >= 3
PY3K3 = sys.version_info[:2] >= (3, 3)

"""
Organization of code:
 - Exceptions
 - Add the compatibility functions to support both 2 & 3 versions.
"""


#--------------------------------------------------------------------------
# Exceptions
#--------------------------------------------------------------------------
class NoDependencyError(Exception):
    def __init__(self, dep_name):
        self.dep_name = dep_name
        self.msg = "The dependency: {0!r} is not available, please install."
        self.msg = self.msg.format(dep_name)

#--------------------------------------------------------------------------
# Use functions for grouping the code for the dependencies
#--------------------------------------------------------------------------
def StringIO():  # noqa
    if PY3K:
        from io import StringIO
    else:
        # Get best StringIO possible!
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
    return StringIO

def mock():  # noqa
    if PY3K3:
        import unittest.mock as mock
    else:
        try:
            import mock
        except ImportError:
            raise NoDependencyError('mock')
    return mock

StringIO = StringIO()
mock = mock()
