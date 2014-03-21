"""Delete all unnecessary files and directories in repository
"""
import os
import fnmatch
import shutil
from os.path import join, realpath

BASE_DIR = realpath(join(__file__, "..", ".."))

FOLDER_PATTERNS = ["__pycache__", "build", "dist"]
FILE_PATTERNS = [
    "*.out", "*.pyc", "*.pyo", "*parsetab.py", "*lextab.py"
]


def matches_any_pattern(name, patterns):
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def is_in_folder(name, path):
    return path.endswith(os.sep + name) or os.sep + name + os.sep in path


def should_remove_folder(root, name):
    return matches_any_pattern(name, FOLDER_PATTERNS)


def should_remove_file(root, name):
    return (
        matches_any_pattern(name, FILE_PATTERNS) or
        (
            root.endswith(os.path.join("py2c", "syntax_tree")) and
            name.endswith(".py") and
            name != "__init__.py"
        )
    )


def main():
    for root, dirs, files in os.walk(BASE_DIR, topdown=False):
        if is_in_folder(".git", root):
            continue

        for name in dirs:
            if should_remove_folder(root, name):
                print("Removing Folder:", join(root, name))
                shutil.rmtree(join(root, name))

        for name in files:
            if should_remove_file(root, name):
                fname = join(root, name)
                print("Removing File:", fname)
                os.remove(fname)


if __name__ == '__main__':
    main()
