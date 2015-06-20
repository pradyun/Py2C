"""Unit-tests for `py2c.abc.manager.Manager`
"""

from py2c.tests import Test
from nose.tools import assert_raises

from py2c.abc.manager import Manager


# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------
class GoodManager(Manager):
    options = {}

    def run(self, node):
        pass


class EmptyManager(Manager):
    pass


class NoRunManager(Manager):
    options = {}


class NoOptionsManager(Manager):
    def run(self, node):
        pass


class OptionsNotADictManager(Manager):
    options = object()  # Not instance of dict

    def run(self, node):
        pass


class SuperCallingManager(Manager):
    options = {}

    def run(self, node):
        super().run(node)


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestBaseManager(Test):
    """py2c.abc.manager.Manager
    """

    def test_initializes_a_subclass_with_all_required_methods(self):
        GoodManager()

    def check_bad_initialization(self, manager_class, err, required_phrases):
        with assert_raises(err) as context:
            manager_class()

        self.assert_error_message_contains(context.exception, required_phrases)

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

    def test_recognizes_subclass(self):
        assert issubclass(GoodManager, Manager), "Did not recognize subclass"

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
