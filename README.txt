Decorator module
=================

Dependencies:

The decorator module requires Python 2.4.

Installation
-------------

If you are lazy, just perform

$ easy_install decorator

which will install just the module on your system. Notice that
Python 3 requires the easy_install version of the distribute_ project.

If you prefer to install the full distribution from source, including
the documentation, download the tarball_, unpack it and run

$ python setup.py install

in the main directory, possibly as superuser.

.. _tarball: http://pypi.python.org/pypi/decorator
.. _distribute: http://packages.python.org/distribute/

Testing
--------

For Python 2.4, 2.5, 2.6, 2.7 run

$ python documentation.py

for Python 3.X run

$ python documentation3.py

You will see a few innocuous errors with Python 2.4 and 2.5, because
some inner details such as the introduction of the ArgSpec namedtuple 
and Thread.__repr__ changed. You may safely ignore them.
Notice that you may run into trouble if in your system there is an older version
of the decorator module; in such a case remove the old version.

Documentation
--------------

There are various versions of the documentation:

-  `HTML version (Python 2)`_ 
-  `PDF version (Python 2)`_ 

-  `HTML version (Python 3)`_ 
-  `PDF version (Python 3)`_ 

.. _HTML version (Python 2): http://micheles.googlecode.com/hg/decorator/documentation.html
.. _PDF version (Python 2): http://micheles.googlecode.com/hg/decorator/documentation.pdf
.. _HTML version (Python 3): http://micheles.googlecode.com/hg/decorator/documentation3.html
.. _PDF version (Python 3): http://micheles.googlecode.com/hg/decorator/documentation3.pdf
