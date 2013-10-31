"""Runs tests in a directory.
"""
import os, unittest

def main():
    unittest.TextTestRunner(verbosity=1).run(
        unittest.defaultTestLoader.discover(
            os.path.dirname(__file__), "test_*.py"
        )
    )

if __name__ == "__main__":
    main()
