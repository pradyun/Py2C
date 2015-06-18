#!/usr/bin/env python3
"""Run tests.

Whether run from the terminal (by developer or CI) or from the editor,
this file makes sure the tests are run in a similar manner every-time.
"""

# Standard library
import sys
from os.path import join, realpath, dirname

# Third Party modules
import nose
import coverage

# NOTE:: Haven't added a proper CLI to this file because mixing the CLI with
#        coverage, nose and remove_files.py is a complicated problem.
#        On the other hand, using source argument for coverage works just fine.
_dev_tools_dir = realpath(dirname(__file__))

COVERAGERC_FILE = join(_dev_tools_dir, ".coveragerc")
TEST_DIRECTORY = join(dirname(_dev_tools_dir), "py2c")

GENERATE_REPORT = True
GENERATE_REPORT_HTML = True
GENERATE_REPORT_TEXT = True


def run_tests():
    # Any arguments that start with "py2c" or None if no such arguments exist
    source = list(filter(lambda x: x.startswith("py2c"), sys.argv[1:])) or None

    cov = coverage.coverage(config_file=COVERAGERC_FILE, source=source)
    cov.start()
    success = nose.run(
        env={
            "NOSE_INCLUDE_EXE": "True",
            "NOSE_WITH_HTML_REPORT": "True",
            "NOSE_HTML_OUTPUT_FILE": "/tmp/test-html/index.html",
            "NOSE_WITH_SPECPLUGIN": "True"
        },
        defaultTest=TEST_DIRECTORY,
    )
    cov.stop()
    cov.save()

    if GENERATE_REPORT or success:
        if GENERATE_REPORT_HTML:
            cov.html_report()
        if GENERATE_REPORT_TEXT:
            cov.report()
    sys.exit(0 if success else 1)


def main():
    run_tests()

if __name__ == '__main__':
    main()
