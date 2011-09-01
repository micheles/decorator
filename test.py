"""
Some simple tests executable with nose or py.test
"""

import os
from decorator import decorator

@decorator
def identity(f, *a, **k):
    "do nothing decorator"
    return f(*a, **k)

@identity
def f1():
    "f1"

def getfname(func):
    fname = os.path.basename(func.func_globals['__file__'])
    return os.path.splitext(fname)[0] + '.py'

def test0():
    this = getfname(identity)
    assert this == 'test.py', this
    print(identity.__doc__)

def test1():
    this = getfname(f1)
    assert this == 'test.py', this
    print(f1.__doc__)
