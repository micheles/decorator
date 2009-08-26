try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '3.1.2'

if __name__ == '__main__':
    try:
        docfile = file('/tmp/documentation.html')
    except IOError: # file not found, ignore
        doc = ''
    else:
        doc = docfile.read()
    setup(name='decorator',
          version=VERSION,
          description='Better living through Python with decorators',
          long_description='</pre>%s<pre>' % doc,
          author='Michele Simionato',
          author_email='michele.simionato@gmail.com',
          url='http://pypi.python.org/pypi/decorator',
          license="BSD License",
          py_modules = ['decorator'],
          keywords="decorators generic utility",
          platforms=["All"],
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities'],
          zip_safe=False)

