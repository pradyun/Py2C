"""Runs tests in this directory.

It runs the tests and checks the code-coverage.

* Not used for 'setup.py test'
"""
import os
import time
import unittest
from os.path import join, dirname, realpath

CHECK_COVERAGE = True

try:
    import coverage
except ImportError:
    HAVE_COVERAGE = False
else:
    HAVE_COVERAGE = True


class CoverageTester(object):
    """docstring for CoverageTester"""
    def __init__(self, *args, **kwargs):
        super(CoverageTester, self).__init__()
        if HAVE_COVERAGE and CHECK_COVERAGE:
            self.cov = coverage.coverage(*args, **kwargs)
        else:
            self.cov = None

    def __enter__(self):
        if self.cov is not None:
            self.cov.start()
        return self.cov

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cov is not None:
            self.cov.stop()
        return exc_type is not None


def load():
    return unittest.defaultTestLoader.discover(
        os.path.dirname(__file__), "test_*.py"
    )


def run(suite, *args, **kwargs):
    return unittest.TextTestRunner(*args, **kwargs).run(suite)


def main(*args, **kwargs):
    with CoverageTester() as cov:
        run(load(), *args, **kwargs)

    if cov is None:
        return

    # In Sublime Text 2, helps prevent mixing of outputs
    time.sleep(0.1)
    src_path = join(dirname(dirname(realpath(__file__))), "py2c")

    cov.exclude(r'if\s+__name__\s*==\s*.__main__.:', which='exclude')
    cov.exclude(r'return[ ]+not[ ]+\w+[ ]*==[ ]*\w+', which='exclude')

    cov.report(
        omit=[
            "*parsetab.py",
            os.path.join(src_path, "dual_ast.py"),
            os.path.join(src_path, "python_builtins.py"),
        ],
        include=[src_path + "*"]
    )
    cov.html_report()

if __name__ == "__main__":
    main(buffer=True)
