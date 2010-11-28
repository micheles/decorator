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

def test0():
    assert os.path.basename(identity.func_globals['__file__']) == 'test.py'
    print identity.__doc__

def test1():
    assert os.path.basename(f1.func_globals['__file__']) == 'test.py'
    print f1.__doc__

