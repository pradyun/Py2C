#!/usr/bin/env python3
"""Delete all unnecessary files and directories in repository
"""

import os
import shutil
import fnmatch
import argparse
from os.path import join, relpath


FOLDER_PATTERNS = ["__pycache__", "build", "dist", "test-report"]
FILE_PATTERNS = [
    # Git
    "*.orig",
    # PLY
    "*.out", "*parsetab.py", "*lextab.py",
    # Coverage
    ".coverage",
    # Sublime Text
    "*.fuse_hidden*",
    # setup.py left-overs
    "*.egg", "*.tar.gz"
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
        root.endswith(os.path.join("py2c", "tree")) and
        name.endswith(".py") and
        name not in ["__init__.py", "node_gen.py", "visitors.py"]
    )


def remove_files(directory, remove_generated, verbosity, dry_run):
    if verbosity > 0:
        if dry_run:
            print("(Dry-Run) ", end="")
        print("Cleaning {}...".format(directory))

    for root, dirs, files in os.walk(directory, topdown=False):
        if is_in_folder(".git", root):
            continue

        for dir_name in dirs:
            if should_remove_folder(root, dir_name):
                dir_path = join(root, dir_name)

                if verbosity > 0:
                    print("Deleting Folder:", relpath(dir_path, directory))
                if not dry_run:
                    shutil.rmtree(dir_path)

        for file_name in files:
            if should_remove_file(root, file_name) or (remove_generated and is_generated_file(root, file_name)):  # noqa
                file_path = join(root, file_name)

                if verbosity > 1:
                    print("Deleting File  :", relpath(file_path, directory))
                if not dry_run:
                    os.remove(file_path)


# -----------------------------------------------------------------------------
# CLI stuff
# -----------------------------------------------------------------------------
def setup_parser(parser):
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


def main(argv=None):
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    args = parser.parse_args(argv)

    verbosity = max(args.verbose - args.quiet, 0)
    remove_files(
        args.directory, args.remove_generated, verbosity, args.dry_run
    )


if __name__ == '__main__':
    main()
