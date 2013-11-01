#!/usr/bin/env python
"""This module contains pure-python implementations of the built-in functions.
DON'T add any other functions to this file. ONLY built-in functions.
"""

def any(iterable):
    """any(iterable) -> bool

    Return True if bool(x) is True for any x in the iterable.
    If the iterable is empty, return False."""
    for item in iterable:
        if item:
            return True
    return False

def all(iterable):
    """any(iterable) -> bool

    Return True if bool(x) is True for all values x in the iterable.
    If the iterable is empty, return False."""
    for item in iterable:
        if not item:
            return False
    return True

def sum(iterable, start=0):
    """sum(sequence[, start]) -> value

    Returns the sum of the items of a sequence plus the value
    of parameter 'start' (which defaults to 0).  When the sequence is
    empty, returns start."""
    total = start
    for item in iterable:
        total += item
    return total

def range(start, stop=None, step=1):
    """range(stop) -> list of integers
    range(start, stop[, step]) -> list of integers

    Return a list containing an arithmetic progression of integers.
    range(i, j) returns [i, i+1, i+2, ..., j-1]; start (!) defaults to 0.
    When step is given, it specifies the increment (or decrement).
    For example, range(4) returns [0, 1, 2, 3].  The end point is omitted!
    These are exactly the valid indices for a list of 4 elements."""
    if stop is None:
        stop = start
        start = 0
    if step == 0:
        raise ValueError("step argument should not be zero")
    if (step > 0 and start >= stop) or (step < 0 and start <= stop):
        return []

    retval = []
    i = start
    while (i < stop if step > 0 else i > stop):
        retval.append(i) # yield i
        i += step
    return retval

def enumerate(iterable, start=0):
    """enumerate(iterable[, start]) -> iterator for index, value of iterable

    Return an enumerate object.  iterable must be another object that supports
    iteration.  The enumerate object yields pairs containing a count (from
    start, which defaults to zero) and a value yielded by the iterable argument.
    enumerate is useful for obtaining an indexed list:
        (0, seq[0]), (1, seq[1]), (2, seq[2]), ..."""
    retval = []
    for o in iterable[start:]:
        retval.append((start,o)) # yield (start,o)
        start += 1
    return retval

def filter(func, iterable):
    """filter(function or None, sequence) -> list, tuple, or string

    Return those items of sequence for which function(item) is true.  If
    function is None, return the items that are true.  If sequence is a tuple
    or string, return the same type, else return a list."""
    if func is None:
        func = lambda x: x
    retval = []
    for item in iterable:
        if func(item):
            retval.append(item) # yield item
    return retval

