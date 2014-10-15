#!/usr/bin/env python3
"""Run tests under a consistent environment...
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import os
import sys
from os.path import join, realpath, dirname

# Third Party modules
import nose
import coverage

# Local stuff
import html_runner


base_dir = realpath(dirname(__file__))
test_dir = join(dirname(base_dir), "py2c")

cov = coverage.coverage(config_file=join(base_dir, ".coveragerc"))

html_plugin = html_runner.HTMLOutputNosePlugin()
cov.start()
success = nose.run(
    env={"NOSE_INCLUDE_EXE": "True", "NOSE_WITH_HTML_GEN": "True"},
    defaultTest=test_dir,
    addplugins=[html_plugin],
    # argv=["foo", "--help"]
)
cov.stop()
cov.save()

if success:
    # If we are in CI environment, don't write an HTML report.
    if os.environ.get("CI", None) is None:
        cov.html_report()
    print()
    cov.report()

sys.exit(0 if success else 1)
