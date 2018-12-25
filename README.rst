Decorator module
=================

:Author: Michele Simionato
:E-mail: michele.simionato@gmail.com
:Requires: Python from 2.6 to 3.7
:Download page: http://pypi.python.org/pypi/decorator
:Installation: ``pip install decorator``
:License: BSD license

Installation
-------------

If you are lazy, just perform

 `$ pip install decorator`

which will install just the module on your system.

If you prefer to install the full distribution from source, including
the documentation, clone the `GitHub repo`_ or download the tarball_, unpack it and run

 `$ pip install .`

in the main directory, possibly as superuser.

.. _tarball: http://pypi.python.org/pypi/decorator
.. _GitHub repo: https://github.com/micheles/decorator

Testing
--------

If you have the source code installation you can run the tests with

 `$ python src/tests/test.py -v`

or (if you have setuptools installed)

 `$ python setup.py test`

Notice that you may run into trouble if in your system there
is an older version of the decorator module; in such a case remove the
old version. It is safe even to copy the module `decorator.py` over
an existing one, since we kept backward-compatibility for a long time.

Repository
---------------

The project is hosted on GitHub. You can look at the source here:

 https://github.com/micheles/decorator

Documentation
---------------

The documentation has been moved to http://decorator.readthedocs.io/en/latest/
You can download a PDF version of it from http://media.readthedocs.org/pdf/decorator/latest/decorator.pdf

For the impatient
-----------------

Here is an example of how to define a family of decorators tracing slow
operations:

.. code-block:: python

   from decorator import decorator

   @decorator
   def warn_slow(func, timelimit=60, *args, **kw):
       t0 = time.time()
       result = func(*args, **kw)
       dt = time.time() - t0
       if dt > timelimit:
           logging.warn('%s took %d seconds', func.__name__, dt)
       else:
           logging.info('%s took %d seconds', func.__name__, dt)
       return result

   @warn_slow  # warn if it takes more than 1 minute
   def preprocess_input_files(inputdir, tempdir):
       ...

   @warn_slow(timelimit=600)  # warn if it takes more than 10 minutes
   def run_calculation(tempdir, outdir):
       ...

Enjoy!

