#!/bin/bash -e

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# A script that generates the source distribution in a clean venv and tests it.
# Requires:
#   - virtualenvwrapper to be installed and source'd beforehand.
#   - Current working directory is the root of the project.
#------------------------------------------------------------------------------

# TODO: Convert into a pure-python script (using subprocess)
RED=1
GREEN=2
YELLOW=3

write_text() {
    level=$1
    if [ $level == $RED ]; then
        echo -e -n "\e[1;31m$2\e[0m"
    elif [ $level == $GREEN ]; then
        echo -e -n "\e[1;32m$2\e[0m"
    elif [ $level == $YELLOW ]; then
        echo -e -n "\e[1;33m$2\e[0m"
    else
        echo "(Unknown color) $2"
    fi
}

delete_venv() {
    write_text $1 "Deleting temporary virtualenv\n"
    deactivate > /dev/null
}

# Create a temporary venv (with virtualenvwrapper) and come back to same directory
write_text $YELLOW "Making temporary virtualenv for the build\n"
pushd /tmp > /dev/null
mktmpenv
popd > /dev/null

write_text $YELLOW "Cleaning project..."
python dev_tools/cleanup.py all > /dev/null 2> /dev/null || return 1
write_text $GREEN "done\n"

write_text $YELLOW "Installing build requirements\n"
write_text $YELLOW "    ply..."
pip install -q ply
if [ $? != 0 ]; then
    write_text $RED "failed\n"
    delete_venv $RED
    return 1
fi
write_text $GREEN "done\n"

write_text $YELLOW "Building source distribution\n"
python setup.py sdist > /dev/null
if [ $? != 0 ]; then
    write_text $RED "Couldn't build source distribution!\n"
    delete_venv $RED
    return 1
fi

write_text $YELLOW "Installing source distribution\n"
pip install dist/*.tar.gz
if [ $? != 0 ]; then
    write_text $RED "Couldn't install package...\n"
    delete_venv $RED
    return 1
fi

write_text $YELLOW "Check: Is the package installed? "
python -c "import py2c" 2> /dev/null
if [ $? != 0 ]; then
    write_text $RED "No!\n"
    delete_venv $RED
    return 1
else
    write_text $GREEN "Yes!\n"
fi

write_text $YELLOW "Check: Is the auto-generated file generated, importable? "
python -c "import py2c.syntax_tree.python" 2> /dev/null
if [ $? != 0 ]; then
    write_text $RED "No!\n"
    delete_venv $RED
    return 1
else
    write_text $GREEN "Yes!\n"
fi

write_text $YELLOW "Installing requirements for testing\n"

write_text $YELLOW "    nose..."
pip install -q nose
if [ $? != 0 ]; then
    write_text $RED "failed\n"
    delete_venv $RED
    return 1
fi
write_text $GREEN "done\n"

write_text $YELLOW "\nRunning Tests\n"
nosetests py2c

delete_venv $YELLOW
