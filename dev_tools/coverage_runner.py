"""Run tests under coverage's measurement system
"""
from os.path import join, realpath

import nose
import coverage

cov = coverage.coverage(branch=True)

cov.start()
nose.run(defaultTest=realpath(join(__file__, "..", "..", "py2c")))
cov.stop()
cov.save()
cov.html_report()
