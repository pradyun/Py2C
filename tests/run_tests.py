"""Runs tests in a directory.
"""
import os, unittest

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=1).run(
        unittest.defaultTestLoader.discover(
            os.path.dirname(__file__), "test_*.py"
        )
    )
