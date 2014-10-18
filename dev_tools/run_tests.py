#!/usr/bin/env python3
"""Run tests under a consistent environment...
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import sys
from os.path import join, realpath, dirname

# Third Party modules
import nose
import coverage

base_dir = realpath(dirname(__file__))
root_dir = join(dirname(base_dir), "py2c")

cov = coverage.coverage(config_file=join(base_dir, ".coveragerc"))
cov.start()
success = nose.run(
    env={"NOSE_INCLUDE_EXE": "True", "NOSE_WITH_HTML_REPORT": "True"},
    defaultTest=root_dir,
    # argv=["foo", "--help"]
)
cov.stop()
cov.save()

if success:
    cov.html_report()
    cov.report()

sys.exit(0 if success else 1)
