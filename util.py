"""
A few useful decorators
"""

import sys, time
from decorator import decorator

@decorator
def traced(func, *args, **kw):
    t1 = time.time()
    res = func(*args,**kw)
    t2 = time.time()
    print >> sys.stderr, func.__name__, args, 'TIME:', t2-t1
    return res
