def any(iterable):
    for item in iterable:
        if item:
            return True
    return False
def all(iterable):
    for item in iterable:
        if not item:
            return False
    return True
def sum(iterable,start = 0):
    sum_ = start
    for item in iterable:
        sum_ += item
    return sum_
