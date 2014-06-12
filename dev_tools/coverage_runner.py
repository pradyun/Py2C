"""Run tests under coverage's measurement system
"""

import os
import sys
from os.path import join, realpath

# Third Party modules
import nose
import coverage

base_dir = realpath(join(__file__, ".."))
cov = coverage.coverage(config_file=join(base_dir, ".coveragerc"))

cov.start()
success = nose.run(defaultTest=join(base_dir, ".."))
cov.stop()
cov.save()

if success:
    # If we are in CI environment, don't write an HTML report.
    if os.environ.get("CI", None) is None:
        cov.html_report()
    # Just write the report anyway.
    cov.report()

sys.exit(0 if success else 1)
