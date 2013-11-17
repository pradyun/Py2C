import sys
sys.argv.extend("egg_info".split())

from setuptools import setup

# Description of package
description = (
    "A Translator for translating implicitly statically typed Python "
    "code into human-readable C code"
)

long_description = open("README.md").read()

# Metadata
classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Programming Language :: C',
    'Programming Language :: C++',
    # Supports Python 2.7 & 3.3 only (Might work with other versions though)
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
    packages=["py2c"],
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
    classifiers=classifiers
)
