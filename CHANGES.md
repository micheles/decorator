HISTORY
--------

## Unreleased

## 4.0.10 (2016-06-07)

Improved the documentation thanks to Tony Goodchild (zearin) who also
provided a much better CSS than the one I was using.

## 4.0.9 (2016-02-08)

Same as 4.0.7 and 4.0.8, re-uploaded due to issues on PyPI.

## 4.0.7 (2016-02-06)

Switched to a new changelog format (the one in http://keepachangelog.com/)
since it was contributed by Alexander Artemenko. Re-added a newline to support
old version of Python, as requested by [azjps](https://github.com/azjps).

## 4.0.6 (2015-12-11)

Removed a file x.py accidentally entered in the tarball.

## 4.0.5 (2015-12-09)

Documented a quirk signaled by David Goldstein when writing decorators
for functions with keyword arguments. Avoided copying the globals,
as signaled by Benjamin Peterson.

## 4.0.4 (2015-09-25)

Included a patch from Zev Benjamin: now decorated functions play well
with cProfile.

## 4.0.3 (2015-09-25)

Added a warning about the memoize example, as requested by Robert
Buchholz.

## 4.0.2 (2015-07-28)

docs/README.rst was not included in MANIFEST.in by accident,
thus breaking the source installation.

## 4.0.1 (2015-07-28)

Added docs directory and upload_docs command. Fixed bug with
`__qualname__`, reported by Lucian Petrut.

## 4.0.0 (2015-07-24)

Removed the need for 2to3 by dropping the support for Python 2.5.
Added a MANIFEST.in file and produced a proper wheel. Improved
the integration with setuptools so that `python setup.py test` works.
Reworked the documentation and introduced `decorator.decorated`.
Removed any dependence from `inspect.getargspec`, which is deprecated
in Python 3.5, as signaled by Ralf Gommers.
Fixed `contextmanager` to work with Python 3.5.
Copied the `__qualname__` attribute, as requested by Frazer McLean.
Added a `dispatch_on` facility to implement generic functions.

## 3.4.2 (2015-03-22)

Same as 3.4.1, re-uploaded to PyPI.

## 3.4.1 (2015-03-16)

Ported the repository from GoogleCode to GitHub and added Travis CI
support. Tests are executed with the new command `python test.py -v`.
setuptools is now mandatory in Python 3. The suggested
installation tool is now `pip`, not `easy_install`. Supported IronPython
and other Python implementations without sys._getframe, as requested by
Doug Blank.

## 3.4.0 (2012-10-18)

Added the ability to use classes and generic callables as callers and
implemented a signature-preserving contexmanager decorator. Fixed a bug
with the signature f(**kw) in Python 3 and fixed a couple of doctests
broken by Python 3.3, both issues pointed out by Dominic Sacré.

## 3.3.3 (2012-04-23)

Fixed a bug with kwonlyargs for Python 3, submitted by Chris
Ellison.

## 3.3.2 (2011-09-01)

Fixed a bug with __kwdefaults__ for Python 3, submitted by Chris
Ellison.

## 3.3.1 (2011-04-22)

Fixed a doctest broken for Python 3.2, as noted by
Arfrever Frehtes Taifersar Arahesis; changed the name of
the attribute ``undecorated`` to ``__wrapped__``, by following the
Python 3.2 convention, as requested by Ram Rachum; added
the Python 3 classifier to setup.py.

## 3.3 (2011-01-01)

Added support for function annotations.

## 3.2.1 (2010-12-28)

Now the .func_globals of the decorated function are the same of
the undecorated function, as requested by Paul Ollis.

## 3.2 (2010-05-22)

Added __version__ (thanks to Gregg Lind), removed functionality which 
has been deprecated for years, removed the confusing decorator_factory
example and added official support for Python 3 (requested by Claus Klein).
Moved the documentation from PyPI to googlecode.

## 3.1.2 (2009-08-25)

Added attributes args, varargs, keywords and arg0, ..., argN
to FunctionMaker objects generated from a function; fixed another
Pylons-breaking bug signaled by Lawrence Oluyede.

## 3.1.1 (2009-08-18)

Fixed a bug which was breaking Pylons, signaled by
Gabriel de Perthuis, and added a test for it.

## 3.1 (2009-08-16)

Added decorator.factory, an easy way to define families of decorators
(requested by various users, including David Laban). Refactored the
FunctionMaker class and added an easier to use .create classmethod.
Internally, functools.partial is used for Python >= 2.5.

## 3.0.1 (2009-02-16)

Improved the error message in case a bound/unbound method is passed
instead of a function and documented this case; that should make life
easier for users like Gustavo Nerea.

## 3.0 (2008-12-14)

New major version introducing ``FunctionMaker`` and the two-argument
syntax for ``decorator``. Moreover, added support for getting the
source code. This version is Python 3.0 ready.  Major overhaul of the
documentation, now hosted on http://packages.python.org/decorator.

## 2.3.2 (2008-12-01)

Small optimization in the code for decorator factories. First version
with the code uploaded to PyPI.

## 2.3.1 (2008-07-25)

Set the zipsafe flag to False, since I want my users to have the source,
not a zipped egg.

## 2.3.0 (2008-07-10)

Added support for writing decorator factories with minimal effort
(feature requested by Matthew Wilson); implemented it by enhancing
'decorator' to a Python 2.6 class decorator.

## 2.2.0. (2007-07-31)

Added a note on 'inspect.getsource' not working for decorated
functions; referenced PEP 326; highlighted the snippets in the 
documentation with pygments; slightly simplified the code.

## 2.1.0. (3/07/2007)

Replaced the utility 'update_wrapper' with 'new_wrapper' and
updated the documentation accordingly; fixed and improved the 
doctester argument parsing, signaled by Sam Wyse.

## 2.0.1 (2007-02-17)

Included the licence in the source code too; fixed a versioning
issue by adding the version number to the zip file and fixing
the link to it on the web page, thanks to Philip Jenvey.

## 2.0 (2007-01-13)

Rewritten and simplified the implementation; broken compatibility
with previous versions (in minor ways); added the utility function
'update_wrapper' instead of 'newfunc'.

## 1.1 (2006-12-02)

'decorator' instances now have attributes __name__, __doc__,
__module__ and __dict__ coming from the associated caller function; 
included the licence into the documentation.

## 1.0 (2006-08-10)

Added LICENSE.txt; added a setuptools-friendly setup.py script 
contributed by Luke Arno.

## 0.8.1 (2006-06-21)

Minor fixes to the documentation.

## 0.8 (2006-06-16)

Improved the documentation, added the 'caveats' section.

## 0.7.1 (2006-05-15)

Improved the tail_recursive example.

## 0.7 (2006-05-10)

Renamed 'copyfunc' into 'newfunc' and added the ability to copy
the signature from a model function;   improved '_decorator' to
set the '__module__' attribute too, with the intent of improving 
error messages; updated the documentation.

## 0.6 (2005-12-20)

Changed decorator.__call__ so that the module somewhat works
even for Python 2.3 (but the signature-preserving feature is
lost).

## 0.5.2 (2005-06-28)

Minor changes to the documentation; improved `getattr_` and
shortened `locked`.

## 0.5.1 (2005-05-20)

Minor corrections to the documentation.

## 0.5 (2005-05-19)

Fixed a bug with out-of-the-mind signatures, added a check for
reserved names in the argument list and simplified the code (thanks to
Duncan Booth).

## 0.4.1 (2005-05-17)

Fixed a typo in the documentation (thanks to Anthon van der Neut).

## 0.4 (2005-05-12)

Added getinfo, some tests and improved the documentation.

## 0.3 (2005-05-10)

Simplified copyfunc, renamed deferred to delayed and added the
nonblocking example.

## 0.2 (2005-05-09)

Added copyfunc, improved the multithreading examples, improved the
doctester program.

## 0.1.1 (2005-05-06)

Added the license specification and two docstrings.

## 0.1 (2005-05-04)

Initial release.
