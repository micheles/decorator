Decorator module
=================

:Author: Michele Simionato
:E-mail: michele.simionato@gmail.com
:Requires: Python 2.4+
:Download page: http://pypi.python.org/pypi/decorator
:Installation: ``pip install decorator``
:License: BSD license

Installation
-------------

If you are lazy, just perform

 `$ pip install decorator`

which will install just the module on your system.

If you prefer to install the full distribution from source, including
the documentation, download the tarball_, unpack it and run

 `$ python setup.py install`

in the main directory, possibly as superuser.

.. _tarball: http://pypi.python.org/pypi/decorator
.. _distribute: http://packages.python.org/distribute/

Testing
--------

Run

 `$ python test.py -v`

You will see a few innocuous errors with Python 2.5, because some
inner details such as the introduction of the ArgSpec namedtuple and
Thread.__repr__ changed. You may safely ignore them. 

You cannot run the tests in Python 2.4, since there is a test using
the with statement, but the decorator module is expected to work
anyway (it has been used in production with Python 2.4 for years). My
plan is to keep supporting all Python versions >= 2.4 in the core
module, but I will keep the documentation and the tests updated only
for the latest Python versions in both the 2.X and 3.X branches.

Finally, notice that you may run into trouble if in your system there
is an older version of the decorator module; in such a case remove the
old version.

Documentation
--------------

There are various versions of the documentation:

-  `HTML version (Python 2)`_ 
-  `PDF version (Python 2)`_ 

-  `HTML version (Python 3)`_ 
-  `PDF version (Python 3)`_ 

.. _HTML version (Python 2): https://github.com/micheles/decorator/blob/3.4.2/documentation.rst
.. _PDF version (Python 2): https://github.com/micheles/decorator/blob/3.4.2/documentation.pdf
.. _HTML version (Python 3): https://github.com/micheles/decorator/blob/3.4.2/documentation3.rst
.. _PDF version (Python 3): https://github.com/micheles/decorator/blob/3.4.2/documentation3.pdf

Repository
---------------

The project is hosted on GitHub. You can look at the source here:

 https://github.com/micheles/decorator
