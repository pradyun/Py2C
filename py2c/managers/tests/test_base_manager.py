"""Tests for the ABC of Manager
"""

#------------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
#------------------------------------------------------------------------------

from py2c.managers.base_manager import BaseManager

from py2c.tests import Test
from nose.tools import assert_raises


#------------------------------------------------------------------------------
# Helper classes
#------------------------------------------------------------------------------
class GoodManager(BaseManager):
    options = {}

    def run(self, node):
        pass


class EmptyManager(BaseManager):
    pass


class NoRunManager(BaseManager):
    options = {}


class NoOptionsManager(BaseManager):

    def run(self, node):
        pass


class OptionsNotADictManager(BaseManager):
    options = object()  # Not instance of dict

    def run(self, node):
        pass


class SuperCallingManager(BaseManager):
    options = {}

    def run(self, node):
        super().run(node)


#------------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------------
class TestBaseManager(Test):
    """Tests for Managers
    """

    def test_initialization_of_a_well_formed_manager(self):
        GoodManager()

    def check_bad_initialization(self, manager_class, err, required_phrases):
        with assert_raises(err) as context:
            manager_class()

        self.assert_message_contains(context.exception, required_phrases)

    def test_bad_initialization(self):
        yield from self.yield_tests(self.check_bad_initialization, [
            (
                "without options attribute and without run method",
                EmptyManager, TypeError, ["EmptyManager"]
            ),
            (
                "without run method",
                NoRunManager, TypeError, ["NoRunManager", "run"]
            ),
            (
                "without options attribute",
                NoOptionsManager, AttributeError,
                ["NoOptionsManager", "options", "attribute"]
            ),
            (
                "with a non-dictionary options attribute",
                OptionsNotADictManager, TypeError,
                ["OptionsNotADictManager", "options", "should be", "instance", dict.__qualname__] # noqa
            ),
        ], described=True, prefix="initialization of manager ")

    def test_manager_with_super_calling_run_method(self):
        manager = SuperCallingManager()

        with assert_raises(NotImplementedError):
            manager.run(object())

if __name__ == '__main__':
    from py2c.tests import runmodule
    runmodule()
