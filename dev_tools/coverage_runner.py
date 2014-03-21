"""Run tests under coverage's measurement system
"""
import nose
import coverage
from os.path import join, realpath

cov = coverage.coverage(branch=True, config_file=True)

cov.start()
result = nose.run(defaultTest=realpath(join(__file__, "..", "..")))
cov.stop()
cov.html_report()
