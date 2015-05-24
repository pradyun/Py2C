"""Tests for the ABC of Worker
"""

# -----------------------------------------------------------------------------
# Py2C - A Python to C++ compiler
# Copyright (C) 2014 Pradyun S. Gedam
# -----------------------------------------------------------------------------

from py2c.base_worker import BaseWorker

from py2c.tests import Test
from nose.tools import assert_raises


# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------
class GoodWorker(BaseWorker):

    def work(self):
        pass


class BadWorker(BaseWorker):
    pass


class SuperCallingWorker(BaseWorker):

    def work(self):
        super().work()


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestBaseWorker(Test):
    """base_worker.BaseWorker
    """

    def test_does_initialize_a_subclass_with_work_method(self):
        GoodWorker()

    def check_bad_initialization(self, manager_class, err, required_phrases):
        with assert_raises(err) as context:
            manager_class()

        self.assert_message_contains(context.exception, required_phrases)

    def test_does_not_do_bad_initialization(self):
        yield from self.yield_tests(self.check_bad_initialization, [
            (
                "without work method",
                BadWorker, TypeError, ["BadWorker", "work"]
            ),
        ], described=True, prefix="does not initialize subclass ")

    def test_blocks_subclass_with_calling_super_work_method(self):
        manager = SuperCallingWorker()

        with assert_raises(NotImplementedError):
            manager.work()


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
