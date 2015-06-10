"""Unit-tests for :class:`py2c.managers.base_manager.BaseManager`
"""

from py2c.tests import Test
from nose.tools import assert_raises

from py2c.managers.base_manager import BaseManager


# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestBaseManager(Test):
    """base_manager.BaseManager
    """

    def test_does_initialize_a_subclass_with_options_and_run_attributes(self):
        GoodManager()

    def check_bad_initialization(self, manager_class, err, required_phrases):
        with assert_raises(err) as context:
            manager_class()

        self.assert_message_contains(context.exception, required_phrases)

    def test_does_not_do_bad_initialization(self):
        yield from self.yield_tests(self.check_bad_initialization, [
            (
                "without options attribute or run method",
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
                [
                    "OptionsNotADictManager", "options", "should be",
                    "instance", dict.__qualname__
                ]
            ),
        ], described=True, prefix="does not initialize subclass ")

    def test_blocks_subclass_with_calling_super_run_method(self):
        manager = SuperCallingManager()

        with assert_raises(NotImplementedError):
            manager.run(object())


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
