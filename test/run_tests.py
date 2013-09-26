"""Runs tests in a directory.
"""
import os, unittest

unittest.TextTestRunner().run(
    unittest.defaultTestLoader.discover(os.path.dirname(__file__), "test_*.py")
)
