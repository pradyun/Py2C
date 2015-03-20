#!/usr/bin/env python3
"""Delete all unnecessary files and directories in repository
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

import os
import sys
import shutil
import fnmatch
import argparse
from os.path import join, relpath

PRINT_OUTPUT = True
REMOVE_GENERATED_AST = len(sys.argv) > 1 and sys.argv[1].lower() == "all"

FOLDER_PATTERNS = ["__pycache__", "build", "dist", "test-report"]
FILE_PATTERNS = [
    "*.out", "*.pyc", "*.pyo", "*parsetab.py", "*lextab.py", ".coverage",
    "*.fuse_hidden*", "*.egg", "*.tar.gz"
]


def matches_any_pattern(name, patterns):
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def is_in_folder(name, path):
    return path.endswith(os.sep + name) or os.sep + name + os.sep in path


def should_remove_folder(root, name):
    return matches_any_pattern(name, FOLDER_PATTERNS)


def should_remove_file(root, name):
    return (
        matches_any_pattern(name, FILE_PATTERNS)
    )


def is_generated_file(root, name):
    return (
        REMOVE_GENERATED_AST and
        root.endswith(os.path.join("py2c", "tree")) and
        name.endswith(".py") and
        name not in ["__init__.py", "node_gen.py", "visitors.py"]
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        help="Directory to be cleaned",
        nargs="?", default=os.getenv("PWD", os.getcwd())
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Increase verbosity (can be repeated)",
        action="count", default=2
    )
    parser.add_argument(
        "-q", "--quiet",
        help="Decrease verbosity (can be repeated)",
        action="count", default=0
    )
    parser.add_argument(
        "-n", "--dry-run",
        help="Only print, don't delete anything.",
        action="store_true"
    )
    parser.add_argument(
        "-a", "--remove-generated", "--all",
        help="Remove auto-generated AST files too.",
        action="store_true"
    )
    return parser.parse_args()


def remove_files(args):
    if args.verbosity > 0:
        if args.dry_run:
            print("(Dry-Run) ", end="")
        print("Cleaning {}...".format(args.directory))

    for root, dirs, files in os.walk(args.directory, topdown=False):
        if is_in_folder(".git", root):
            continue

        for dir_name in dirs:
            if should_remove_folder(root, dir_name):
                dir_path = join(root, dir_name)

                if args.verbosity > 0:
                    print("Deleting Folder:", relpath(dir_path, args.directory))  # noqa
                if not args.dry_run:
                    shutil.rmtree(dir_path)

        for file_name in files:
            print(root, file_name)
            if should_remove_file(root, file_name) or (args.remove_generated and is_generated_file(root, file_name)):  # noqa
                file_path = join(root, file_name)

                if args.verbosity > 1:
                    print("Deleting File  :", relpath(file_path, args.directory))  # noqa
                if not args.dry_run:
                    os.remove(file_path)


def cleanup_args(args):
    args.verbosity = max(args.verbose - args.quiet, 0)


def main():
    args = parse_args()
    cleanup_args(args)
    remove_files(args)

if __name__ == '__main__':
    main()
