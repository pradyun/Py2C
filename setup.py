# import sys
# sys.argv.extend("test".split())

from setuptools import setup, find_packages

#--------------------------------------------------------------------------
# Description of package
description = (
    "An translator to translate implicitly statically typed Python code into "
    "human-readable C++ code."
)

long_description = open("README.md").read()

# Metadata
classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Programming Language :: C++',
    # Support for Python 2.7 & 3.3 guarenteed
    # Might support other versions, but not so sure (yet).
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Topic :: Software Development :: Code Generators',
    'Topic :: Software Development :: Compilers',
]

# The main setup call
setup(
    # Package data
    name="py2c",
    version="0.1dev",
    packages=find_packages(exclude=["tests"]),
    package_data={
        'py2c': ['_ast_nodes.cfg'],  # include the configration file
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
    test_suite="tests",
)
