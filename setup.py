from setuptools import setup

dic = dict(__file__=None)
exec(open('src/decorator.py').read(), dic)  # extract the __version__
VERSION = dic['__version__']


if __name__ == '__main__':
    setup(name='decorator',
          version=VERSION,
          description='Decorators for Humans',
          long_description=open('README.rst').read(),
          author='Michele Simionato',
          author_email='michele.simionato@gmail.com',
          url='https://github.com/micheles/decorator',
          license="BSD-2-Clause",
          package_dir={'': 'src'},
          py_modules=['decorator'],
          keywords="decorators generic utility",
          platforms=["All"],
          python_requires='>=3.7',
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: BSD License',
                       'Natural Language :: English',
                       'Operating System :: OS Independent',
                       'Programming Language :: Python',
                       'Programming Language :: Python :: 3.8',
                       'Programming Language :: Python :: 3.9',
                       'Programming Language :: Python :: 3.10',
                       'Programming Language :: Python :: 3.11',
                       'Programming Language :: Python :: 3.12',
                       'Programming Language :: Python :: 3.13',
                       'Programming Language :: Python :: Implementation :: CPython',
                       'Topic :: Software Development :: Libraries',
                       'Topic :: Utilities'],
          test_suite='tests',
          zip_safe=False)
