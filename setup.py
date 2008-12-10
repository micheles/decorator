try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = '3.0.0'

if __name__ == '__main__':
    setup(name='decorator',
          version=VERSION,
          description='Better living through Python with decorators',
          long_description="""\
    As of now, writing custom decorators correctly requires some experience 
    and it is not as easy as it could be. For instance, typical implementations
    of decorators involve nested functions, and we all know 
    that flat is better than nested. Moreover, typical implementations
    of decorators do not preserve the signature of decorated functions,
    thus confusing both documentation tools and developers.

    The aim of the decorator module it to simplify the usage of decorators 
    for the average programmer, and to popularize decorators usage giving 
    examples of useful decorators, such as memoize, tracing, threaded, etc.""",
          author='Michele Simionato',
          author_email='michele.simionato@gmail.com',
          url='http://pypi.python.org/pypi/decorator',
          license="BSD License",
          py_modules = ['decorator'],
          keywords="decorators generic utility",
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities'],
            zip_safe=False)

