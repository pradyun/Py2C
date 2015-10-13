"""Unit-tests for `py2c.abc.manager.Manager`
"""

from py2c.tests import Test, data_driven_test
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

initialization_invalid_cases = [
    {
        "description": "without options attribute or run method",
        "args": [
            EmptyManager, TypeError, ["EmptyManager"]
        ]
    },
    {
        "description": "without run method",
        "args": [
            NoRunManager, TypeError, ["NoRunManager", "run"]
        ]
    },
    {
        "description": "without options attribute",
        "args": [
            NoOptionsManager, AttributeError,
            ["NoOptionsManager", "options", "attribute"]
        ]
    },
    {
        "description": "with a non-dictionary options attribute",
        "args": [
            OptionsNotADictManager, TypeError,
            [
                "OptionsNotADictManager", "options", "should be", "instance",
                "dict"
            ]
        ]
    },
]


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestBaseManager(Test):
    """py2c.abc.manager.Manager
    """

    def test_initializes_a_subclass_with_all_required_methods(self):
        GoodManager()

    @data_driven_test(initialization_invalid_cases, prefix="raises error initializing: ")
    def test_initialization_invalid_cases(self, manager_class, err, required_phrases):
        with assert_raises(err) as context:
            manager_class()

        self.assert_error_message_contains(context.exception, required_phrases)

    def test_blocks_subclass_with_calling_super_run_method(self):
        manager = SuperCallingManager()

        with assert_raises(NotImplementedError):
            manager.run(object())

    def test_recognizes_subclass(self):
        assert issubclass(GoodManager, Manager), "Did not recognize subclass"

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
