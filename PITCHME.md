# The decorator module is alive and kicking

+++

Have you ever heard of the decorator module?

+++

Have you ever heard of IPython?

+++

Every time to fire an IPython instance you are importing
the decorator module :-)

+++

Several frameworks and tools depend on it, so it is one of the most
downloaded packages on PyPI

+++
**Famous last words**

decorator 0.1, May 2005: *this is a hack, surely they will fix the signature
in the next release of Python*

...

+++

# or maybe no

+++?image=releases.png

+++

**It is joy to maintain**

- next to zero bugs
- I get few questions
- I usually implement something new only when there is new Python release

+++

For instance

- Python 3.4 generic functions => decorator 4.0
- Python 3.5/3.6 async/await => decorator 4.1
- Python 3.7 dataclasses => decorator 4.2

---

The recommended way to write decorators in Python

```python
from functools import wraps

def trace(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        print('Calling', f.__name__)
        return f(*args, **kwds)
    return wrapper

@trace
def add(x, y):
    """Sum two numbers"""
    return x + y
```
+++
The problem is that it does not really work

```python
>>> inspect.getfullargspec(add)
FullArgSpec(args=[], varargs='args', varkw='kwds',
            defaults=None, kwonlyargs=[],
            kwonlydefaults=None, annotations={})
```
and inspect.getfullargspec is telling the truth
```
>>> add.__code__.co_varnames
('args', 'kwds')
```
---

Enter the decorator module
```python
from decorator import decorator

@decorator
def trace(f, *args, **kwds):
    print('Calling', f.__name__)
    return f(*args, **kwds)

@trace
def add(a, b):
    return a + b

>>> add.__code__.co_varnames
('a', 'b')
```

---

Since 2017 you can also decorate coroutines
```python
@decorator
async def trace(coro, *args, **kwargs):
    print('Calling %s', coro.__name__)
    await coro(*args, **kwargs)

@trace
async def make_task(n):
    for i in range(n):
        await asyncio.sleep(1)

```
---

```python
import warnings
from decorator import decorator

@decorator
def deprecated(func, message='', *args, **kw):
    msg = '%s.%s has been deprecated. %s' % (
        func.__module__, func.__name__, message)
    if not hasattr(func, 'called'):
        warnings.warn(msg, DeprecationWarning, stacklevel=2)
        func.called = 0
    func.called += 1
    return func(*args, **kw)

@deprecated('Use new_function instead')
def old_function():
   'Do something'
```
---
http://decorator.readthedocs.io/en/latest/
