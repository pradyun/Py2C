#!/usr/bin/python
import sys
from setuptools import setup, find_packages


description = (
    "A translator to translate implicitly statically typed Python code into "
    "(hopefully) human-readable C++ code."
)

long_description = open("README.md").read()

# Metadata
classifiers = [
    'Development Status :: 1 - Planning',
    'Programming Language :: C++',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Compilers',
]

# For running tests
tests_require = ["nose"]
if sys.version_info[:2] < (3, 3):
    tests_require.extend([
        "mock",
    ])

sys.argv.append("build")
# The main setup call
setup(
    # Package data
    name="py2c",
    version="0.1-dev",
    packages=find_packages(exclude=["tests"]),
    package_data={
        'py2c': ['*.ast'],  # include the declaration files
    },
    install_requires=["ply"],
    zip_safe=False,
    # Metadata
    description=description,
    long_description=long_description,
    author="Pradyun S. Gedam",
    author_email="pradyunsg@gmail.com",
    url="https://github.com/pradyun/Py2C",
    classifiers=classifiers,
    # Testing
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite="nose.collector",
)
