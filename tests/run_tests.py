"""Runs tests in a directory.
"""
import os, unittest
from os.path import join, dirname, realpath

CHECK_COVERAGE = True

try:
    import coverage
except ImportError:
    HAVE_COVERAGE = False
else:
    HAVE_COVERAGE = True

def main():
    if HAVE_COVERAGE and CHECK_COVERAGE:
        cov = coverage.coverage()
        cov.start()
    unittest.TextTestRunner(verbosity=1).run(
        unittest.defaultTestLoader.discover(
            os.path.dirname(__file__), "test_*.py"
        )
    )
    if HAVE_COVERAGE and CHECK_COVERAGE:
        cov.stop()
        import time
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
            include=[
                src_path + "*"
            ]

        )
        cov.html_report()

if __name__ == "__main__":
    main()
