#!/usr/bin/env python3
"""Run tests under coverage's measurement system
"""

import os
import sys
from os.path import join, realpath, dirname

# Third Party modules
import nose
import coverage

base_dir = realpath(dirname(__file__))
test_dir = join(dirname(base_dir), "py2c")

cov = coverage.coverage(config_file=join(base_dir, ".coveragerc"))

cov.start()
success = nose.run(env={"NOSE_INCLUDE_EXE": "True"}, defaultTest=test_dir)
cov.stop()
cov.save()

if success:
    # If we are in CI environment, don't write an HTML report.
    if os.environ.get("CI", None) is None:
        cov.html_report()
        if False:
            os.system("firefox _coverage_reports/index.html 2> /dev/null")
    print()
    cov.report()

sys.exit(0 if success else 1)
