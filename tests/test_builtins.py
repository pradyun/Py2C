#!/usr/bin/env python

import sys
import unittest

import py2c.python_builtins as python_builtins


@unittest.skip("Not ready to use!")
class BuiltinsTestCase(unittest.TestCase):
    """Tests for Built-ins defined in Pure Python"""

    def test_range(self):
        range = python_builtins.range
        self.assertEqual(range(3), [0, 1, 2])
        self.assertEqual(range(1, 5), [1, 2, 3, 4])
        self.assertEqual(range(0), [])
        self.assertEqual(range(-3), [])
        self.assertEqual(range(1, 10, 3), [1, 4, 7])
        self.assertEqual(range(5, -5, -3), [5, 2, -1, -4])

        # Now test range() with longs
        self.assertEqual(range(-2**100), [])
        self.assertEqual(range(0, -2**100), [])
        self.assertEqual(range(0, 2**100, -1), [])
        self.assertEqual(range(0, 2**100, -1), [])

        a = long(10 * sys.maxint)
        b = long(100 * sys.maxint)
        c = long(50 * sys.maxint)

        self.assertEqual(range(a, a+2), [a, a+1])
        self.assertEqual(range(a+2, a, -1), [a+2, a+1])
        self.assertEqual(range(a+4, a, -2), [a+4, a+2])

        seq = range(a, b, c)
        self.assertIn(a, seq)
        self.assertNotIn(b, seq)
        self.assertEqual(len(seq), 2)

        seq = range(b, a, -c)
        self.assertIn(b, seq)
        self.assertNotIn(a, seq)
        self.assertEqual(len(seq), 2)

        seq = range(-a, -b, -c)
        self.assertIn(-a, seq)
        self.assertNotIn(-b, seq)
        self.assertEqual(len(seq), 2)

        self.assertRaises(TypeError, range)
        self.assertRaises(TypeError, range, 1, 2, 3, 4)
        self.assertRaises(ValueError, range, 1, 2, 0)
        self.assertRaises(ValueError, range, a, a + 1, long(0))

        class badzero(int):
            def __cmp__(self, other):
                raise RuntimeError
            __hash__ = None  # Invalid cmp makes this unhashable
        self.assertRaises(RuntimeError, range, a, a + 1, badzero(1))

        # Reject floats.
        self.assertRaises(TypeError, range, 1., 1., 1.)
        self.assertRaises(TypeError, range, 1e100, 1e101, 1e101)

        self.assertRaises(TypeError, range, 0, "spam")
        self.assertRaises(TypeError, range, 0, 42, "spam")

        self.assertRaises(OverflowError, range, -sys.maxint, sys.maxint)
        self.assertRaises(OverflowError, range, 0, 2*sys.maxint)

        bignum = 2*sys.maxint
        smallnum = 42

        # Old-style user-defined class with __int__ method
        class I0:
            def __init__(self, n):
                self.n = int(n)

            def __int__(self):
                return self.n
        self.assertEqual(range(I0(bignum), I0(bignum + 1)), [bignum])
        self.assertEqual(range(I0(smallnum), I0(smallnum + 1)), [smallnum])

        # New-style user-defined class with __int__ method
        class I1(object):
            def __init__(self, n):
                self.n = int(n)

            def __int__(self):
                return self.n
        self.assertEqual(range(I1(bignum), I1(bignum + 1)), [bignum])
        self.assertEqual(range(I1(smallnum), I1(smallnum + 1)), [smallnum])

        # New-style user-defined class with failing __int__ method
        class IX(object):
            def __int__(self):
                raise RuntimeError
        self.assertRaises(RuntimeError, range, IX())

        # New-style user-defined class with invalid __int__ method
        class IN(object):
            def __int__(self):
                return "not a number"
        self.assertRaises(TypeError, range, IN())

        # Exercise various combinations of bad arguments, to check
        # refcounting logic
        self.assertRaises(TypeError, range, 0.0)

        self.assertRaises(TypeError, range, 0, 0.0)
        self.assertRaises(TypeError, range, 0.0, 0)
        self.assertRaises(TypeError, range, 0.0, 0.0)

        self.assertRaises(TypeError, range, 0, 0, 1.0)
        self.assertRaises(TypeError, range, 0, 0.0, 1)
        self.assertRaises(TypeError, range, 0, 0.0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0, 1)
        self.assertRaises(TypeError, range, 0.0, 0, 1.0)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1)
        self.assertRaises(TypeError, range, 0.0, 0.0, 1.0)


if __name__ == '__main__':
    unittest.main()
