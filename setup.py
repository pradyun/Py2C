from setuptools import setup, find_packages

import sys;sys.argv.append("develop")

# $TODO Add metadata

description = (
    "A Translator for translating implicitly statically typed Python "
    "code into human-readable C code"
)

setup(
    name="py2c",
    version="0.1a",
    packages=["py2c"],
    description=description,
    long_description=open("README.md").read(),
    zip_safe=False,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
)
