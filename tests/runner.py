"""Runs tests in this directory.

It runs the tests and checks the code-coverage.

* Not used for 'setup.py test'
"""
import unittest
from os.path import join, dirname, realpath

try:
    import coverage
except ImportError:
    CHECK_COVERAGE = False
else:
    CHECK_COVERAGE = True


class CoverageTextTestRunner(unittest.TextTestRunner):
    """A test runner that runs the tests with coverage checking
    """
    py2c_source_base = join(dirname(dirname(realpath(__file__))), "py2c")

    exclude_patterns = [
        r'if\s+__name__\s*==\s*.__main__.:',
        r'return[ ]+not[ ]+\w+[ ]*==[ ]*\w+'
    ]

    ignored_files = ["*parsetab.py", "_dual_ast.py", "python_builtins.py"]

    def run(self, test):
        if not CHECK_COVERAGE:
            return super().run(test)
        else:
            cov = coverage.coverage()

            cov.start()
            retval = super().run(test)
            cov.stop()

            for pattern in self.exclude_patterns:
                cov.exclude(pattern, which="exclude")

            cov.report(
                omit=self.ignored_files,
                include=[self.py2c_source_base + "*"]
            )
            return retval

if __name__ == '__main__':
    tests = unittest.defaultTestLoader.discover(
        dirname(__file__), "test_*.py"
    )
    CoverageTextTestRunner().run(tests)
