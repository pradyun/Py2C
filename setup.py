#!/usr/bin/python3
# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

# pylint:disable=C0103
import sys

if sys.version_info[:2] < (3, 3):
    print("Cannot run on Python versions before Python 3.3")
    sys.exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
    # Include Py2C to tell the user that it is us writing that message.
    print("[Py2C] Please install 'setuptools'..")
    sys.exit(1)

# setup.py metadata
from metadata_setup import get_metadata  # noqa
# -----------------------------------------------------------------------------
# Generating the AST
# -----------------------------------------------------------------------------
from os.path import join, dirname, realpath  # noqa

try:  # If ever setuptools improves on the build_py command.
    from setuptools.command.build_py import build_py as _build_py
except ImportError:
    from distutils.command.build_py import build_py as _build_py


class build_py(_build_py):
    """A customized version to build the AST definition files
    """

    def initialize_options(self):
        import py2c.tree.node_gen as node_gen
        path_to_definitions = realpath(join(dirname(__file__), "py2c", "tree"))
        node_gen.generate(path_to_definitions)

        super().initialize_options()


metadata = get_metadata()
# -----------------------------------------------------------------------------
# The main setup call
# -----------------------------------------------------------------------------
setup(
    # Packaging related stuff
    packages=find_packages(),
    setup_requires=["ply==3.4"],
    cmdclass={
        'build_py': build_py,
    },
    **metadata
)
