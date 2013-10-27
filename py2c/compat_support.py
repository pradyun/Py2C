"""
Contains the compatibility related stuff to allow for compatibility across\
Python versions"""
import sys

# Compatibility across versions
PY3K = sys.version_info[0] >= 3

# Use functions for groupong the code
def StringIO():
    if PY3K:
        from io import StringIO
    else:
        # Get best StringIO possible!
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO
    return StringIO

StringIO = StringIO()
