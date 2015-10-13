#!/usr/bin/env python3
"""Build the distribution and check that it passes the tests.
"""

import sys
import glob
import shlex
import contextlib
import subprocess
from subprocess import DEVNULL

# Output
COLOR_CODES = {
    "error": [1, 31],
    "success": [32],
    "info": [33],
    "important_info": [1, 33]
}

# Debugging
RUN = True
DEBUG = False

# Dependencies
TEST_DEPENDENCIES = ["ply", "nose", "coverage", "spec"]

WHEEL_BASED_DISTRIBUTION = {
    "type": "wheel",
    "dependencies": ["wheel"],
    "build_command": "bdist_wheel",
    "file_glob": "*.whl",
}
SOURCE_BASED_DISTRIBUTION = {
    "type": "source",
    "dependencies": [],
    "build_command": "sdist",
    "file_glob": "*.tar.gz",
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def log(color, *args):
    if color is not None:
        print("\033[", ";".join(map(str, COLOR_CODES[color])), "m", sep="", end="")
    print(*args, sep="", end="")
    if color is not None:
        print("\033[0m", end="")
    sys.stdout.flush()

    return True  # Allows use as log(xyz) and fail()


def run(command, should_show_output=False, shell=True):
    if DEBUG:
        print(command, end=";")
        sys.stdout.flush()
    if RUN:
        if not shell:
            command = shlex.split(command)
        if should_show_output:
            returncode = subprocess.call(command, shell=shell)
        else:
            returncode = subprocess.call(
                command, stdout=DEVNULL, stderr=DEVNULL, shell=shell
            )
        return not returncode
    return True


def fail(fail_message=None):
    if fail_message is not None:
        log("error", fail_message)
    raise Exception()


def run_and_report(msg, error_msg, success_msg, command, should_show_output=False):
    log("info", msg)
    OK = run(command, should_show_output)
    if not OK:
        log("error", error_msg, "\n")
        fail()
    else:
        log("success", success_msg, "\n")


# -----------------------------------------------------------------------------
# Shorthands
# -----------------------------------------------------------------------------
def install_dependency(name):
    run_and_report(
        "   " + name + "...",
        "Couldn't install!", "Done!",
        "pip install -q {}".format(name), False
    )


def uninstall_dependency(name):
    run_and_report(
        "   " + name + "...",
        "Couldn't uninstall!", "Done!",
        "pip uninstall -q -y {}".format(name), False
    )


# -----------------------------------------------------------------------------
# Abstractions
# -----------------------------------------------------------------------------
def success_log(*args, important=False):
    log("important_info" if important else "info", *args)
    try:
        yield
    except Exception:
        log("error", *args)
        raise
    else:
        log("success", *args)


def clean_project():
    run_and_report(
        "Cleaning project...", "Couldn't clean!", "Done!",
        "{} dev-tools/cleanup.py all".format(sys.executable), False
    )


def _manage_dependencies(func, message, type_, dependencies):
    log("info", message.format(type_))
    if not dependencies:
        log("success", "None needed!")
    print()
    sys.stdout.flush()
    for dependency in dependencies:
        func(dependency)


def install_dependencies(type_, dependencies):
    _manage_dependencies(
        install_dependency, "Installing {} dependencies...",
        type_, dependencies
    )


def uninstall_dependencies(type_, dependencies):
    _manage_dependencies(
        uninstall_dependency, "Uninstalling {} dependencies...",
        type_, dependencies
    )


def run_tests():
    log("important_info", "Running tests...")
    print()  # For some reason, needed to prevent color-leaks
    sys.stdout.flush()
    run("nosetests --exe py2c", True, True)


def run_basic_checks():
    # Basic checks
    run_and_report(
        "Check: Is project installed? ",
        "Couldn't import project!", "Yes!",
        "{} -c 'import py2c'".format(sys.executable)
    )
    run_and_report(
        "Check: Is auto-generated file usable? ",
        "No!", "Yes!",
        "{} -c 'import py2c.tree.python'".format(sys.executable)
    )


def build_distribution(distribution):
    # Build
    run_and_report(
        "Building {} distribution...".format(distribution["type"]),
        "Failed!", "Done!",
        "{} setup.py {}".format(
            sys.executable, distribution["build_command"]
        )
    )


def install_distribution(distribution):
    # Install
    run_and_report(
        "Installing {} distribution...".format(distribution["type"]),
        "Failed to install!", "Done!",
        "{0} -m pip install {1}".format(
            sys.executable, glob.glob("./dist/" + distribution["file_glob"])[0]
        )
    )


@contextlib.contextmanager
def dependencies_installed(type_, dependencies):
    install_dependencies(type_, dependencies)
    try:
        yield
    finally:
        uninstall_dependencies(type_, dependencies)


def build_install_test_package(distribution):
    log("info", "-"*80 + "\n")
    log("info", "Checking the {} build\n".format(distribution["type"]))
    log("info", "-"*80 + "\n")
    clean_project()
    # Build
    with dependencies_installed("build-time ({})".format(distribution["type"]), distribution["dependencies"]):  # noqa
        build_distribution(distribution)
    # Install
    install_distribution(distribution)

    # Testing
    run_basic_checks()
    with dependencies_installed("test", TEST_DEPENDENCIES):
        run_tests()

    run("cd dev-tools", True)
    # Install
    run_and_report(
        "Uninstalling {} distribution...".format(distribution["type"]),
        "Failed to uninstall!", "Done!",
        "{} -m pip uninstall -q -y py2c".format(sys.executable)
    )
    run("cd ..", True)


def main():
    build_install_test_package(WHEEL_BASED_DISTRIBUTION)
    build_install_test_package(SOURCE_BASED_DISTRIBUTION)


if __name__ == '__main__':
    main()
