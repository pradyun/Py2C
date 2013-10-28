import os
import sys
from setuptools import setup, find_packages

# Description of package
description = (
    "A Translator for translating implicitly statically typed Python "
    "code into human-readable C code"
)

long_description = open("README.md").read()


# The main setup call
setup(
    # Package data
    name="py2c",
    version="0.1dev",
    packages=["py2c"],
    package_data = {
        '': ['*.txt', '*.rst'], # include any *.txt or *.rst files
    },
    install_requires=["ply"],
    zip_safe=False,
    # Metadata
    description=description,
    long_description=long_description,
    author="Ramchandra Apte",
    author_email="maniandram01@gmail.com",
    maintainer="Pradyun S. Gedam",
    maintainer_email="pradyunsg@gmail.com",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
