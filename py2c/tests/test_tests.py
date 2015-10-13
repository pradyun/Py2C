"""Unit-tests for `py2c.tests`
"""

from nose.tools import eq_, assert_is, assert_raises
from py2c.tests import Test, data_driven_test


class TestDataDriven(Test):
    """py2c.tests.data_driven_test
    """

    def test_does_not_yield_values_with_no_arguments(self):
        @data_driven_test([])
        def func():
            pass

        for test in func():
            assert False

    def test_yields_values_in_correct_order_given_arguments(self):
        @data_driven_test([(0,), (1,), (2,)])
        def func(a):
            return a

        iterations = 0
        for test in func():
            assert_equal(test(), iterations)
            iterations += 1

        assert_equal(iterations, 3)

    def test_is_a_generator(self):
        @data_driven_test([[]])
        def func():
            return 1

        obj = func()

        assert_equal(next(obj)(), 1)
        with assert_raises(StopIteration):
            next(obj)

    def test_attaches_proper_description(self):
        test_data = [["Test 0", "argument"], ["Test 1", "argument"]]

        @data_driven_test(test_data, True)
        def func(arg):
            assert_equal(arg, "argument")

        for i, test in enumerate(func()):
            assert_equal(test.description, "Test " + str(i))
            test()

    def test_attaches_prefix_and_suffix_to_description_correctly(self):
        test_data = [["Test 0", "argument"], ["Test 1", "argument"]]

        @data_driven_test(test_data, described=True, prefix="<", suffix=">")
        def func(arg):
            assert_equal(arg, "argument")

        for i, test in enumerate(func()):
            assert_equal(test.description, "<Test {}>".format(i))
            test()

    def test_passes_argument_called_with_to_test_function_when_described(self):
        # This is needed for methods, where "self" argument is passed to
        # the test function
        stub = object()

        test_data = [["Test 0", "argument"], ["Test 1", "argument"]]

        @data_driven_test(test_data, described=True)
        def func(passed, arg):
            assert_is(passed, stub)
            assert_equal(arg, "argument")

        for i, test in enumerate(func(stub)):
            test()

    def test_does_pass_argument_in_call_to_test_function_when_not_described(self):  # noqa
        # This is needed for methods, where "self" argument is passed to
        # the test function
        stub = object()

        test_data = [["argument"]]

        @data_driven_test(test_data)
        def func(passed, arg):
            assert_is(passed, stub)
            assert_equal(arg, "argument")

        for i, test in enumerate(func(stub)):
            test()


class TestAssertMessageContains(Test):
    """py2c.tests.Test.assert_error_message_contains
    """

    def test_does_not_fail_when_given_no_required_phrases(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), []
        )

    def test_matches_complete_phrase_with_same_case(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["Hello World!"]
        )

    def test_does_not_match_complete_phrase_with_different_case(self):
        with assert_raises(AssertionError):
            self.assert_error_message_contains(
                Exception("Hello World!"), ["hello world!"]
            )

    def test_matches_overlapping_partial_phrases(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["lo ", " Wo"]
        )

    def test_matches_non_overlapping_partial_phrases(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["Hello", "World!"]
        )

    def test_matches_regardless_of_order(self):
        self.assert_error_message_contains(
            Exception("Hello World!"), ["World!", "Hello"]
        )


class TestFail(Test):
    """py2c.tests.Test.fail
    """

    def test_does_causes_failure(self):
        with assert_raises(AssertionError):
            self.fail()

    def test_does_raises_exception_with_given_message(self):
        with assert_raises(AssertionError) as context:
            self.fail("EHK14H0b9DXZaT346nqx")  # random text

        eq_(context.exception.args[0], "EHK14H0b9DXZaT346nqx")

        assert context.exception.__cause__ is None

    def test_does_raises_exception_with_given_cause(self):
        err = Exception()
        try:
            raise err
        except Exception as e:
            with assert_raises(AssertionError) as context:
                self.fail(cause=e)

        assert context.exception.__cause__ is err, "Unexpected cause"

    def test_does_honours_keyword_arguments(self):
        err = Exception()
        try:
            raise err
        except Exception as e:
            with assert_raises(AssertionError) as context:
                self.fail(cause=e, message="EHK14H0b9DXZaT346nqx")

        assert context.exception.__cause__ is err, "Unexpected cause"
        eq_(context.exception.args[0], "EHK14H0b9DXZaT346nqx")

if __name__ == '__main__':
    from py2c.tests import runmodule

    runmodule()
