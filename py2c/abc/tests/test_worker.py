"""Unit-tests for `py2c.abc.worker.Worker`
"""

import logging

from py2c.abc.worker import Worker

from py2c.tests import Test, mock
from nose.tools import assert_raises, assert_true, assert_is_instance


# -----------------------------------------------------------------------------
# Helper classes
# -----------------------------------------------------------------------------
class GoodWorker(Worker):
    """A worker so nice, he even logs whenever he's told to work.
    """

    def work(self):
        self.logger.debug("I'm working!")


class BadWorker(Worker):
    pass


class SuperCallingWorker(Worker):

    def work(self):
        super().work()


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
class TestBaseWorker(Test):
    """py2c.abc.worker.Worker
    """

    def test_initializes_a_subclass_with_all_required_methods(self):
        GoodWorker()

    def check_bad_initialization(self, manager_class, err, required_phrases):
        with assert_raises(err) as context:
            manager_class()

        self.assert_error_message_contains(context.exception, required_phrases)

    def test_does_not_do_bad_initialization(self):
        yield from self.yield_tests(self.check_bad_initialization, [
            (
                "without work method",
                BadWorker, TypeError, ["BadWorker", "work"]
            ),
        ], described=True, prefix="does not initialize subclass ")

    def test_blocks_subclass_with_calling_super_work_method(self):
        worker = SuperCallingWorker()

        with assert_raises(NotImplementedError):
            worker.work()

    def test_provides_a_logger_instance_to_subclass_instances(self):
        worker = GoodWorker()

        assert_true(hasattr(worker, 'logger'))
        assert_is_instance(worker.logger, logging.Logger)

        worker.logger = mock.Mock()
        worker.work()

        assert_true(worker.logger.debug.called)

    def test_recognizes_subclass(self):
        assert issubclass(GoodWorker, Worker), "Did not recognize subclass"


if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
