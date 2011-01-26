try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os.path

def getversion(fname):
    """Get the __version__ reading the file: works both in Python 2.X and 3.X,
    whereas direct importing would break in Python 3.X with a syntax error"""
    for line in open(fname):
        if line.startswith('__version__'):
            return eval(line[13:])
    raise NameError('Missing __version__ in decorator.py')

VERSION = getversion(
    os.path.join(os.path.dirname(__file__), 'src/decorator.py'))

if __name__ == '__main__':
    setup(name='decorator',
          version=VERSION,
          description='Better living through Python with decorators',
          long_description=open('README.txt').read(),
          author='Michele Simionato',
          author_email='michele.simionato@gmail.com',
          url='http://pypi.python.org/pypi/decorator',
          license="BSD License",
          package_dir = {'': 'src'},
          py_modules = ['decorator'],
          keywords="decorators generic utility",
          platforms=["All"],
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 3',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities'],
          use_2to3=True,
          zip_safe=False)
