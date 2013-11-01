
from setuptools import setup

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
    package_data={
        '': ['*.cfg'],  # include any configration files
    },
    install_requires=["ply"],
    zip_safe=False,
    # Metadata
    description=description,
    long_description=long_description,
    author="Pradyun S. Gedam",
    author_email="pradyunsg@gmail.com",
    url="https://github.com/pradyun/Py2C",
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
