#!/usr/bin/env python3
"""Build the distribution and check that it passes the tests.
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

import sys
import shlex
import subprocess
from subprocess import DEVNULL

# Output
COLOR_CODES = {
    "error": 31,
    "success": 32,
    "report": 33
}

# Debugging
DEBUG = False

# Dependencies
BUILD_DEPENDENCIES = []
TEST_DEPENDENCIES = ["ply", "nose", "coverage"]


#------------------------------------------------------------------------------
# Helpers
#------------------------------------------------------------------------------
def log(color, *args):
    if color is not None:
        print("\033[1;", COLOR_CODES[color], "m", sep="", end="")
    print(*args, sep="", end="")
    if color is not None:
        print("\033[0m", end="")
    sys.stdout.flush()

    return True  # Allows use as log(xyz) and fail()


def run(command, should_show_output=True):
    if not DEBUG:
        if should_show_output:
            returncode = subprocess.call(shlex.split(command))
        else:
            returncode = subprocess.call(
                shlex.split(command), stdout=DEVNULL, stderr=DEVNULL
            )
        return not returncode
    return True


def fail(fail_message=None):
    if fail_message is not None:
        log("error", fail_message)
    raise Exception()


def run_and_report(msg, error_msg, success_msg, command, should_show_output=True):
    log("report", msg)
    OK = run(command, should_show_output)
    if not OK:
        log("error", error_msg, "\n")
        fail()
    else:
        log("success", success_msg, "\n")


#------------------------------------------------------------------------------
# Shorthands
#------------------------------------------------------------------------------
def install_dependency(name):
    run_and_report(
        "   " + name + "...",
        "Couldn't install!", "Done!",
        "pip install -q {}".format(name)
    )


#------------------------------------------------------------------------------
# Abstractions
#------------------------------------------------------------------------------
def clean_project():
    run_and_report(
        "Cleaning project...", "Couldn't clean!", "Done!",
        sys.executable + " dev_tools/cleanup.py all", False
    )


def install_dependencies(type_, dependencies):
    if not dependencies:
        log("report", "No ", type_, " dependencies.\n")
        return
    log("report", "Installing ", type_, " dependencies:\n")
    for dependency in dependencies:
        install_dependency(dependency)


def install_package():
    run_and_report(
        "Installing package...",
        "Failed to install!", "Done!",
        sys.executable + " setup.py install", False
    )


def basic_installation_checks():
    run_and_report(
        "Check: Is project installed? ",
        "Couldn't import project!", "Yes!",
        sys.executable + " -c 'import py2c'", False
    )

    run_and_report(
        "Check: Is auto-generated file usable? ",
        "No!", "Yes!",
        sys.executable + " -c 'import py2c.ast.python'", False
    )


def test_package():
    log("report", "Running tests...")
    print()
    run("nosetests --exe py2c")


def main():
    clean_project()

    install_dependencies("build", BUILD_DEPENDENCIES)
    install_package()
    basic_installation_checks()

    install_dependencies("test", TEST_DEPENDENCIES)
    test_package()

if __name__ == '__main__':
    main()
