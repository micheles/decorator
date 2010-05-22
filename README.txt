Decorator module
---------------------------

Dependencies:

The decorator module requires Python 2.4.

Installation:

$ python setup.py install

Testing:

For Python 2.4, 2.5, 2.6, 2.7 run

$ python documentation.py

for Python 3.X run

$ python documentation3.py

You will see a few innocuous errors with Python 2.4 and 2.5, because
some inner details such as the introduction of the ArgSpec namedtuple 
and Thread.__repr__ changed. You may safely ignore them.

Notice:

You may get into trouble if in your system there is an older version
of the decorator module; in such a case remove the old version.

Documentation:

There are two versions of the documentation, one for `Python 2`_ and one
for `Python 3`_ .

.. _Python 2: documentation.html
.. _Python 3: documentation3.html
