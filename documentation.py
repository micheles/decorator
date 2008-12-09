"""\
The ``decorator`` module
=============================================================

:author: Michele Simionato
:E-mail: michele.simionato@gmail.com
:version: 3.0 (11 December 2008)
:Download page: http://pypi.python.org/decorator
:Installation: ``easy_install decorator``
:License: BSD license

.. contents::

Introduction
------------------------------------------------

Python decorators are an interesting example of why syntactic sugar
matters. In principle, their introduction in Python 2.4 changed
nothing, since they do not provide any new functionality which was not
already present in the language; in practice, their introduction has
significantly changed the way we structure our programs in Python. I
believe the change is for the best, and that decorators are a great
idea since:

* decorators help reducing boilerplate code;
* decorators help separation of concerns; 
* decorators enhance readability and maintenability;
* decorators are very explicit.

Still, as of now, writing custom decorators correctly requires
some experience and it is not as easy as it could be. For instance,
typical implementations of decorators involve nested functions, and
we all know that flat is better than nested.

The aim of the ``decorator`` module it to simplify the usage of 
decorators for the average programmer, and to popularize decorators
usage giving examples of useful decorators, such as ``memoize``,
``tracing``, etc.

The core of this module is a decorator factory called ``decorator``. 
All decorators discussed here are built as simple recipes on top 
of  ``decorator``. You may find their source code in the ``documentation.py`` 
file. If you execute it, all the examples contained will be doctested.

Definitions
------------------------------------

Technically speaking, any Python object which can be called with one argument
can be used as  a decorator. However, this definition is somewhat too large 
to be really useful. It is more convenient to split the generic class of 
decorators in two groups:

+ *signature-preserving* decorators, i.e. callable objects taking a
  function as input and returning a function *with the same
  signature* as output;

+ *signature-changing* decorators, i.e. decorators that change
  the signature of their input function, or decorators returning
  non-callable objects.

Signature-changing decorators have their use: for instance the
builtin classes ``staticmethod`` and ``classmethod`` are in this
group, since they take functions and return descriptor objects which 
are not functions, nor callables.

However, signature-preserving decorators are more common and easier to
reason about; in particular signature-preserving decorators can be
composed together whereas other
decorators in general cannot (for instance you cannot 
meaningfully compose a staticmethod with a classmethod or viceversa).

Writing signature-preserving decorators from scratch is not that
obvious, especially if one wants to define proper decorators that 
can accept functions with any signature. A simple example will clarify 
the issue.

Statement of the problem
------------------------------

A typical decorator is a decorator to memoize functions. 
Such a decorator works by caching
the result of a function call in a dictionary, so that the next time
the function is called with the same input parameters the result is retrieved
from the cache and not recomputed. There are many implementations of 
``memoize`` in http://www.python.org/moin/PythonDecoratorLibrary, 
but they do not preserve the signature.
A simple implementation for Python 2.5 could be the following:

$$memoize25

Here we used the ``functools.update_wrapper`` utility, which has
been added in Python 2.5 to simplify the definition of decorators.

The implementation above works in the sense that the decorator 
can accept functions with generic signatures; unfortunately this
implementation does *not* define a signature-preserving decorator, since in
general ``memoize25`` returns a function with a
*different signature* from the original function.

Consider for instance the following case:

>>> @memoize25
... def f1(x):
...     time.sleep(1)
...     return x

Here the original function takes a single argument named ``x``,
but the decorated function takes any number of arguments and
keyword arguments:

>>> from inspect import getargspec 
>>> print getargspec(f1) 
([], 'args', 'kw', None)

This means that introspection tools such as pydoc will give
wrong informations about the signature of ``f1``. This is pretty bad:
pydoc will tell you that the function accepts a generic signature 
``*args``, ``**kw``, but when you try to call the function with more than an 
argument, you will get an error:

>>> f1(0, 1)
Traceback (most recent call last):
   ...
TypeError: f1() takes exactly 1 argument (2 given)

The solution
-----------------------------------------

The solution is to provide a generic factory of generators, which
hides the complexity of making signature-preserving decorators
from the application programmer. The ``decorator`` factory
allows to define decorators without the need to use nested functions 
or classes. 
First of all, you must import ``decorator``:

>>> from decorator import decorator

Then you must define a helper function with signature ``(f, *args, **kw)``
which calls the original function ``f`` with arguments ``args`` and ``kw``
and implements the tracing capability:

$$_memoize

At this point you can define your decorator by means of ``decorator.wrap``:

$$memoize

Here is a test of usage:

>>> @memoize
... def heavy_computation():
...     time.sleep(2)
...     return "done"

>>> print heavy_computation() # the first time it will take 2 seconds
done

>>> print heavy_computation() # the second time it will be instantaneous
done

The signature of ``heavy_computation`` is the one you would expect:

>>> print getargspec(heavy_computation) 
([], None, None, None)

Notice that in general it is impossible to memoize correctly something
that depends on mutable arguments.

A ``trace`` decorator
------------------------------------------------------

As an additional example, here is how you can define a ``trace`` decorator.

$$_trace

$$trace

Then, you can write the following:
 
>>> @trace
... def f1(x):
...     pass

It is immediate to verify that ``f1`` works

>>> f1(0)
calling f1 with args (0,), {}

and it that it has the correct signature:

>>> print getargspec(f1) 
(['x'], None, None, None)

The same decorator works with functions of any signature:

>>> @trace
... def f(x, y=1, z=2, *args, **kw):
...     pass

>>> f(0, 3)
calling f with args (0, 3, 2), {}

>>> print getargspec(f) 
(['x', 'y', 'z'], 'args', 'kw', (1, 2))

That includes even functions with exotic signatures like the following:

>>> @trace
... def exotic_signature((x, y)=(1,2)): return x+y

>>> print getargspec(exotic_signature)
([['x', 'y']], None, None, ((1, 2),))
>>> exotic_signature() 
calling exotic_signature with args ((1, 2),), {}
3

Notice that the support for exotic signatures has been deprecated
in Python 2.6 and removed in Python 3.0.

``decorator`` is a decorator
---------------------------------------------

The ``decorator`` module provides an easy shortcut to convert
the helper function into a signature-preserving decorator: the
``decorator`` function itself, which can be considered as a signature-changing
decorator, just as ``classmethod`` and ``staticmethod``.
However, ``classmethod`` and ``staticmethod`` return generic
objects which are not callable, while ``decorator`` returns
signature-preserving decorators, i.e. functions of a single argument.
Therefore, you can write

>>> @decorator
... def tracing(f, *args, **kw):
...     print "calling %s with args %s, %s" % (f.func_name, args, kw)
...     return f(*args, **kw)

instead of

.. code-block:: python
  
 def _tracing(f, *args, **kw):
     print "calling %s with args %s, %s" % (f.func_name, args, kw)
     return f(*args, **kw)

 def tracing(f):
     return decorator.wrap(_tracing, f)
  
We can easily check that the signature has changed:

>>> print getargspec(tracing)
(['f'], None, None, None)

Therefore now ``tracing`` can be used as a decorator and
the following will work:

>>> @tracing
... def func(): pass

>>> func()
calling func with args (), {}

For the rest of this document, I will discuss examples of useful
decorators built on top of ``decorator``.

``delayed`` and ``threaded``
--------------------------------------------

Often, one wants to define families of decorators, i.e. decorators depending
on one or more parameters. 

Here I will consider the example of a one-parameter family of ``delayed`` 
decorators taking a procedure and converting it into a delayed procedure. 
In this case the time delay is the parameter. 

A delayed procedure is a procedure that, when called, 
is executed in a separate thread after a certain time 
delay. The implementation is not difficult:

$$delayed

Notice that without the help of ``decorator``, an additional level of 
nesting would have been needed.

Delayed decorators as intended to be used on procedures, i.e.
on functions returning ``None``, since the return value of the original 
function is discarded by this implementation. The decorated function returns 
the current execution thread, which can be stored and checked later, for 
instance to verify that the thread ``.isAlive()``.

Delayed procedures can be useful in many situations. For instance, I have used 
this pattern to start a web browser *after* the web server started, 
in code such as

>>> @delayed(2)
... def start_browser():
...     "code to open an external browser window here"

>>> #start_browser() # will open the browser in 2 seconds
>>> #server.serve_forever() # enter the server mainloop

The particular case in which there is no delay is important enough
to deserve a name:

.. code-block:: python

 threaded = delayed(0)

Threaded procedures will be executed in a separated thread as soon
as they are called. Here is an example.

Suppose one wants to write some data to
an external resource which can be accessed by a single user at once
(for instance a printer). Then the access to the writing function must 
be locked:

.. code-block:: python

 import time

 datalist = [] # for simplicity the written data are stored into a list.

$$write

Since the writing function is locked, we are guaranteed that at any given time 
there is at most one writer. Here is an example.

>>> @threaded
... def writedata(data):
...     write(data)

Each call to ``writedata`` will create a new writer thread, but there will 
be no synchronization problems since ``write`` is locked.

>>> writedata("data1") 
<_Timer(Thread-1, started)>

>>> time.sleep(.1) # wait a bit, so we are sure data2 is written after data1

>>> writedata("data2") 
<_Timer(Thread-2, started)>

>>> time.sleep(2) # wait for the writers to complete

>>> print datalist
['data1', 'data2']

``blocking``
-------------------------------------------

Sometimes one has to deal with blocking resources, such as ``stdin``, and
sometimes it is best to have back a "busy" message than to block everything. 
This behavior can be implemented with a suitable decorator:

$$blocking
   
Functions decorated with ``blocking`` will return a busy message if
the resource is unavailable, and the intended result if the resource is 
available. For instance:

>>> @blocking("Please wait ...")
... def read_data():
...     time.sleep(3) # simulate a blocking resource
...     return "some data"

>>> print read_data() # data is not available yet
Please wait ...

>>> time.sleep(1)  
>>> print read_data() # data is not available yet
Please wait ...

>>> time.sleep(1)
>>> print read_data() # data is not available yet
Please wait ...

>>> time.sleep(1.1) # after 3.1 seconds, data is available
>>> print read_data()
some data

decorator factories
--------------------------------------------------------------------

We have already seen examples
of simple decorator factories, implemented as functions returning a
decorator. For more complex situations, it is more convenient to
implement decorator factories as classes returning callable objects
that can be used as signature-preserving decorators.

To give an example of usage, let me
show a (simplistic) permission system based on classes.
Suppose we have a (Web) framework with the following user classes:

$$User
$$PowerUser
$$Admin    

Suppose we have a function ``get_userclass`` returning the class of
the user logged in our system: in a Web framework  ``get_userclass``
will read the current user from the environment (i.e. from REMOTE_USER)
and will compare it with a database table to determine her user class.
For the sake of the example, let us use a trivial function:

$$get_userclass
    
We can implement the ``Restricted`` decorator factory as follows:

$$Restricted
$$PermissionError

An user can perform different actions according to her class:

$$Action

Here is an example of usage::

  >>> a = Action()
  >>> a.view()
  >>> a.insert()   
  Traceback (most recent call last):
    ...
  PermissionError: User does not have the permission to run insert!
  >>> a.delete()   
  Traceback (most recent call last):
    ...
  PermissionError: User does not have the permission to run delete!

A ``PowerUser`` could call ``.insert`` but not ``.delete``, whereas
and ``Admin`` can call all the methods.

I could have provided the same functionality by means of a mixin class
(say ``DecoratorMixin``) providing a ``__call__`` method. Within
that design an user should have derived his decorator class from
``DecoratorMixin``. However, `I generally dislike inheritance`_
and I do not want to force my users to inherit from a class of my
choice. Using the class decorator approach my user is free to use
any class she wants, inheriting from any class she wants, provided
the class provide a proper ``.call`` method and does not provide
a custom ``__call__`` method. In other words, I am trading (less stringent)
interface requirements for (more stringent) inheritance requirements.

.. _I generally dislike inheritance: http://stacktrace.it/articoli/2008/06/i-pericoli-della-programmazione-con-i-mixin1

Dealing with third party decorators: ``decorator.apply``
------------------------------------------------------------

Sometimes you find on the net some cool decorator that you would
like to include in your code. However, more often than not the cool 
decorator is not signature-preserving. Therefore you may want an easy way to 
upgrade third party decorators to signature-preserving decorators without
having to rewrite them in terms of ``decorator``. To this aim the
``decorator`` module provides an utility function
``decorator.apply(third_party_decorator, func)``. 

In order to give an example of usage, I will show a 
pretty slick decorator that converts a tail-recursive function in an iterative
function. I have shamelessly stolen the basic idea from Kay Schluehr's recipe
in the Python Cookbook, 
http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496691.

$$TailRecursive

Here the decorator is implemented as a class returning callable
objects.

$$tail_recursive

Here is how you apply the upgraded decorator to the good old factorial:

.. code-block:: python

 @tail_recursive
 def factorial(n, acc=1):
     "The good old factorial"
     if n == 0: return acc
     return factorial(n-1, n*acc)

 >>> print factorial(4) 
 24

This decorator is pretty impressive, and should give you some food for
your mind ;) Notice that there is no recursion limit now, and you can 
easily compute ``factorial(1001)`` or larger without filling the stack
frame. Notice also that the decorator will not work on functions which
are not tail recursive, such as

$$fact

(a function is tail recursive if it either returns a value without
making a recursive call, or returns directly the result of a recursive
call).

Caveats and limitations
-------------------------------------------

The first thing you should be aware of, it the fact that decorators 
have a performance penalty. 
The worse case is shown by the following example::

 $ cat performance.sh
 python -m timeit -s "
 from decorator import decorator

 @decorator
 def do_nothing(func, *args, **kw):
     return func(*args, **kw) 

 @do_nothing
 def f():
     pass
 " "f()"

 python -m timeit -s "
 def f():
     pass
 " "f()"

On my Linux system, using the ``do_nothing`` decorator instead of the
plain function is more than four times slower::

 $ bash performance.sh 
 1000000 loops, best of 3: 1.68 usec per loop
 1000000 loops, best of 3: 0.397 usec per loop

It should be noted that a real life function would probably do 
something more useful than ``f`` here, and therefore in real life the
performance penalty could be completely negligible.  As always, the
only way to know if there is 
a penalty in your specific use case is to measure it.

You should be aware that decorators will make your tracebacks
longer and more difficult to understand. Consider this example:

>>> @tracing
... def f():
...     1/0

Calling ``f()`` will give you a ``ZeroDivisionError``, but since the
function is decorated the traceback will be longer:

>>> f()
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
    f()
  File "<string>", line 2, in f
  File "<stdin>", line 4, in tracing
    return f(*args, **kw)
  File "<stdin>", line 3, in f
    1/0
ZeroDivisionError: integer division or modulo by zero

You see here the inner call to the decorator ``tracing``, which calls 
``f(*args, **kw)``, and a reference to  ``File "<string>", line 2, in f``. 
This latter reference is due to the fact that internally the decorator
module uses ``exec`` to generate the decorated function. Notice that
``exec`` is *not* responsibile for the performance penalty, since is the
called *only once* at function decoration time, and not every time
the decorated function is called.

Using ``exec`` means that ``inspect.getsource`` will not work for decorated
functions. This means that the usual '??' trick in IPython will give you
the (right on the spot) message 
``Dynamically generated function. No source code available.``. This 
however is preferable to the situation with regular decorators, where 
``inspect.getsource`` gives you the wrapper source code which is probably
not what you want:

$$identity_dec
$$example

>>> import inspect
>>> print inspect.getsource(example)
    def wrapper(*args, **kw):
        return func(*args, **kw)
<BLANKLINE>

(see bug report 1764286_ for an explanation of what is happening).
Actually, starting from release 3.0, the decorator module, adds
a ``__source__`` attribute to the decorated function, therefore
you can get the code which is executed:

>>> print f.__source__
# _call_=<function __main__.tracing>
# _func_=<function __main__.f>
def f():
    return _call_(_func_, )
<BLANKLINE>

.. _1764286: http://bugs.python.org/issue1764286

The generated function is a closure depending on the the caller
``_call_`` and the original function ``_func_``. For debugging convenience
you get the names of the moduled where they are defined in a comment:
in this example they are defined in the ``__main__`` module.

At present, there is no clean way to avoid ``exec``. A clean solution
would require to change the CPython implementation of functions and
add an hook to make it possible to change their signature directly. 
That could happen in future versions of Python (see PEP 362_) and 
then the decorator module would become obsolete. However, at present,
even in Python 3.0 it is impossible to change the function signature
directly, therefore the ``decorator`` module is still useful (this is
the reason why I am releasing version 3.0).

.. _362: http://www.python.org/dev/peps/pep-0362

In the present implementation, decorators generated by ``decorator``
can only be used on user-defined Python functions or methods, not on generic 
callable objects, nor on built-in functions, due to limitations of the
``inspect`` module in the standard library.

Moreover, you can decorate anonymous functions:

>>> tracing(lambda : None)()
calling <lambda> with args (), {}
    
There is a restriction on the names of the arguments: for instance,
if try to call an argument ``_call_`` or ``_func_``
you will get a ``NameError``:

>>> @tracing
... def f(_func_): print f
... 
Traceback (most recent call last):
  ...
NameError: _func_ is overridden in
def f(_func_):
    return _call_(_func_, _func_)

Finally, the implementation is such that the decorated function contains
a copy of the original function attributes:

>>> def f(): pass # the original function
>>> f.attr1 = "something" # setting an attribute
>>> f.attr2 = "something else" # setting another attribute

>>> traced_f = tracing(f) # the decorated function

>>> traced_f.attr1
'something'
>>> traced_f.attr2 = "something different" # setting attr
>>> f.attr2 # the original attribute did not change
'something else'

The ``FunctionMaker`` class
---------------------------------------------------------------

The public API of the ``decorator`` module consists in the
``decorator`` function and its two attributes ``decorator.wrap`` and
``decorator.apply``.  Internally, the functionality is implemented via
a ``FunctionMaker`` class which is able to generate on the fly
functions with a given name and signature. You should not need to
resort to ``FunctionMaker`` when writing ordinary decorators, but it
is interesting to know how the module works internally, so I have
decided to add this paragraph.  Notice that while I do not have plan
to change or remove the functionality provided in the
``FunctionMaker`` class, I do not guarantee that it will stay
unchanged forever. On the other hand, the functionality provided by
``decorator`` has been there from version 0.1 and it is guaranteed to
stay there forever.
``FunctionMaker`` takes the name and the signature of a function in
input, or a whole function. Here is an example of how to
restrict the signature of a function:

>>> def f(*args, **kw):
...     print args, kw

>>> f1 = FunctionMaker(name="f1", signature="a,b").make('''
... def %(name)s(%(signature)s):
...     f(%(signature)s)''', f=f)

>>> f1(1,2)
(1, 2) {}

The utility ``decorator.wrap`` instead takes a function in input and
returns a new function; it is defined as follows:

$$decorator_wrap

Backward compatibility notes
---------------------------------------------------------------

Version 3.0 is a complete rewrite of the original implementation.
It is mostly compatible with the past, a part for a few differences.

The utilites ``get_info`` and ``new_wrapper``, available
in the 2.X versions, have been deprecated and they will be removed
in the future. For the moment, using them raises a ``DeprecationWarning``.
``get_info`` has been removed since it was little used and since it had
to be changed anyway to work with Python 3.0; ``new_wrapper`` has been
removed since it was useless: its major use case (converting
signature changing decorators to signature preserving decorators)
has been subsumed by ``decorator.apply``
and the other use case can be managed with the ``FunctionMaker``.

Finally ``decorator`` cannot be used as a class decorator and the
`functionality introduced in version 2.3`_ has been removed. That
means that in order to define decorator factories with classes you
need to override the ``__call__`` method explicitly (no magic anymore).

All these changes should not cause any trouble, since they were
all rarely used features. Should you have trouble, you are invited to
downgrade to the 2.3 version.

.. _functionality introduced in version 2.3: http://www.phyast.pitt.edu/~micheles/python/documentation.html#class-decorators-and-decorator-factories

LICENCE
---------------------------------------------

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met::

  Redistributions of source code must retain the above copyright 
  notice, this list of conditions and the following disclaimer.
  Redistributions in bytecode form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the
  distribution. 

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
  HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
  DAMAGE.

If you use this software and you are happy with it, consider sending me a 
note, just to gratify my ego. On the other hand, if you use this software and
you are unhappy with it, send me a patch!
"""
from __future__ import with_statement
import sys, threading, time, functools
from decorator import *

decorator_wrap = decorator.wrap

def _trace(f, *args, **kw):
    print "calling %s with args %s, %s" % (f.func_name, args, kw)
    return f(*args, **kw)

def trace(f):
    return decorator.wrap(_trace, f)

def delayed(nsec):
    def _delayed(proc, *args, **kw):
        thread = threading.Timer(nsec, proc, args, kw)
        thread.start()
        return thread
    return decorator(_delayed)

def identity_dec(func):
    def wrapper(*args, **kw):
        return func(*args, **kw)
    return wrapper

@identity_dec
def example(): pass

def _memoize(func, *args, **kw):
    # args and kw must be hashable
    if kw:
      key = args, frozenset(kw.items())
    else:
      key = args
    cache = func.cache  # created at decoration time
    if key in cache:
        return cache[key]
    else:
        cache[key] = result = func(*args, **kw)
        return result

def memoize(f):
    f.cache = {}
    return decorator.wrap(_memoize, f)

def memoize25(func):
    func.cache = {}
    def memoize(*args, **kw):
        if kw:
          key = args, frozenset(kw.items())
        else:
          key = args
        cache = func.cache  # created at decoration time
        if key in cache:
            return cache[key]
        else:
            cache[key] = result = func(*args, **kw)
            return result
    return functools.update_wrapper(memoize, func)

threaded = delayed(0) # no-delay decorator

def blocking(not_avail="Not Available"):
    def _blocking(f, *args, **kw):
        if not hasattr(f, "thread"): # no thread running
            def set_result(): f.result = f(*args, **kw)
            f.thread = threading.Thread(None, set_result)
            f.thread.start()
            return not_avail
        elif f.thread.isAlive():
            return not_avail
        else: # the thread is ended, return the stored result
            del f.thread 
            return f.result
    return decorator(_blocking)

class User(object):
    "Will just be able to see a page"

class PowerUser(User):
    "Will be able to add new pages too"

class Admin(PowerUser):
    "Will be able to delete pages too"

def get_userclass():
    return User

class PermissionError(Exception):
    pass

class Restricted(object):
    """
    Restrict public methods and functions to a given class of users.
    If instantiated twice with the same userclass return the same
    object.
    """
    _cache = {} 
    def __new__(cls, userclass):
        if userclass in cls._cache:
            return cls._cache[userclass]
        self = cls._cache[userclass] = super(Restricted, cls).__new__(cls)
        self.userclass = userclass
        return self
    def call(self, func, *args, **kw):
        userclass = get_userclass()
        if issubclass(userclass, self.userclass):
            return func(*args, **kw)
        else:
            raise PermissionError(
            '%s does not have the permission to run %s!'
            % (userclass.__name__, func.__name__))
    def __call__(self, func):
        return decorator.wrap(self.call, func)

class Action(object):
    @Restricted(User)
    def view(self):
        pass

    @Restricted(PowerUser)
    def insert(self):
        pass

    @Restricted(Admin)
    def delete(self):
        pass
    
class TailRecursive(object):
    """
    tail_recursive decorator based on Kay Schluehr's recipe
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496691
    """
    CONTINUE = object() # sentinel

    def __init__(self, func):
        self.func = func
        self.firstcall = True

    def __call__(self, *args, **kwd):
        try:
            if self.firstcall: # start looping
                self.firstcall = False
                while True:            
                    result = self.func(*args, **kwd)
                    if result is self.CONTINUE: # update arguments
                        args, kwd = self.argskwd
                    else: # last call
                        break
            else: # return the arguments of the tail call
                self.argskwd = args, kwd
                return self.CONTINUE
        except: # reset and re-raise
            self.firstcall = True
            raise
        else: # reset and exit
            self.firstcall = True 
            return result

def tail_recursive(func):
    return decorator.apply(TailRecursive, func)

@tail_recursive
def factorial(n, acc=1):
    "The good old factorial"
    if n == 0: return acc
    return factorial(n-1, n*acc)

def fact(n): # this is not tail-recursive
    if n == 0: return 1
    return n * fact(n-1)

datalist = []

def write(data):
    "Writing to a sigle-access resource"
    with threading.Lock():
        time.sleep(1)
        datalist.append(data)


if __name__ == '__main__':
    import doctest; doctest.testmod()
