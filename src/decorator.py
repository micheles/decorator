# #########################     LICENSE     ############################ #

# Copyright (c) 2005-2018, Michele Simionato
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#   Redistributions in bytecode form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

"""
Decorator module, see http://pypi.python.org/pypi/decorator
for the documentation.
"""
from __future__ import print_function

import re
import sys
import inspect
import operator
import itertools
import collections

__version__ = '4.3.1'

if sys.version >= '3':
    from inspect import getfullargspec

    def get_init(cls):
        return cls.__init__
else:
    FullArgSpec = collections.namedtuple(
        'FullArgSpec', 'args varargs varkw defaults '
        'kwonlyargs kwonlydefaults annotations')

    def getfullargspec(f):
        "A quick and dirty replacement for getfullargspec for Python 2.X"
        return FullArgSpec._make(inspect.getargspec(f) + ([], None, {}))

    def get_init(cls):
        return cls.__init__.__func__

try:
    iscoroutinefunction = inspect.iscoroutinefunction
except AttributeError:
    # let's assume there are no coroutine functions in old Python
    def iscoroutinefunction(f):
        return False
try:
    from inspect import isgeneratorfunction
except ImportError:
    # assume no generator function in old Python versions
    def isgeneratorfunction():
        return False

try:  # python 3.3+
    from inspect import signature
except ImportError:
    from funcsigs import signature


DEF = re.compile(r'\s*def\s*([_\w][_\w\d]*)\s*\(')


# basic functionality
class FunctionMaker(object):
    """
    An object with the ability to create functions with a given signature.
    It has attributes name, doc, module, signature, defaults, dict and
    methods update and make.
    """

    # Atomic get-and-increment provided by the GIL
    _compile_count = itertools.count()

    # make pylint happy
    args = varargs = varkw = defaults = kwonlyargs = kwonlydefaults = ()

    def __init__(self, func=None, name=None, signature=None,
                 defaults=None, doc=None, module=None, funcdict=None):
        self.shortsignature = signature
        if func:
            # func can be a class or a callable, but not an instance method
            self.name = func.__name__
            if self.name == '<lambda>':  # small hack for lambda functions
                self.name = '_lambda_'
            self.doc = func.__doc__
            self.module = func.__module__
            if inspect.isfunction(func):
                argspec = getfullargspec(func)
                self.annotations = getattr(func, '__annotations__', {})
                for a in ('args', 'varargs', 'varkw', 'defaults', 'kwonlyargs',
                          'kwonlydefaults'):
                    setattr(self, a, getattr(argspec, a))
                for i, arg in enumerate(self.args):
                    setattr(self, 'arg%d' % i, arg)
                self.refresh_signature()
                self.dict = func.__dict__.copy()
        # func=None happens when decorating a caller
        if name:
            self.name = name
        if signature is not None:
            self.signature = signature
        if defaults:
            self.defaults = defaults
        if doc:
            self.doc = doc
        if module:
            self.module = module
        if funcdict:
            self.dict = funcdict
        # check existence required attributes
        assert hasattr(self, 'name')
        if not hasattr(self, 'signature'):
            raise TypeError('You are decorating a non function: %s' % func)

    def update(self, func, **kw):
        "Update the signature of func with the data in self"
        func.__name__ = self.name
        func.__doc__ = getattr(self, 'doc', None)
        func.__dict__ = getattr(self, 'dict', {})
        func.__defaults__ = self.defaults
        func.__kwdefaults__ = self.kwonlydefaults or None
        func.__annotations__ = getattr(self, 'annotations', None)
        try:
            frame = sys._getframe(3)
        except AttributeError:  # for IronPython and similar implementations
            callermodule = '?'
        else:
            callermodule = frame.f_globals.get('__name__', '?')
        func.__module__ = getattr(self, 'module', callermodule)
        func.__dict__.update(kw)

    def refresh_signature(self):
        """Update self.signature and self.shortsignature based on self.args,
        self.varargs, self.varkw"""
        allargs = list(self.args)
        allshortargs = list(self.args)
        if self.varargs:
            allargs.append('*' + self.varargs)
            allshortargs.append('*' + self.varargs)
        elif self.kwonlyargs:
            allargs.append('*')  # single star syntax
        for a in self.kwonlyargs:
            allargs.append('%s=None' % a)
            allshortargs.append('%s=%s' % (a, a))
        if self.varkw:
            allargs.append('**' + self.varkw)
            allshortargs.append('**' + self.varkw)
        self.signature = ', '.join(allargs)
        self.shortsignature = ', '.join(allshortargs)

    def make(self, src_templ, evaldict=None, addsource=False, **attrs):
        "Make a new function from a given template and update the signature"
        src = src_templ % vars(self)  # expand name and signature
        evaldict = evaldict or {}
        mo = DEF.search(src)
        if mo is None:
            raise SyntaxError('not a valid function template\n%s' % src)
        name = mo.group(1)  # extract the function name
        names = set([name] + [arg.strip(' *') for arg in
                              self.shortsignature.split(',')])
        for n in names:
            if n in ('_func_', '_call_'):
                raise NameError('%s is overridden in\n%s' % (n, src))

        if not src.endswith('\n'):  # add a newline for old Pythons
            src += '\n'

        # Ensure each generated function has a unique filename for profilers
        # (such as cProfile) that depend on the tuple of (<filename>,
        # <definition line>, <function name>) being unique.
        filename = '<%s:decorator-gen-%d>' % (
            __file__, next(self._compile_count))
        try:
            code = compile(src, filename, 'single')
            exec(code, evaldict)
        except Exception:
            print('Error in generated code:', file=sys.stderr)
            print(src, file=sys.stderr)
            raise
        func = evaldict[name]
        if addsource:
            attrs['__source__'] = src
        self.update(func, **attrs)
        return func

    @classmethod
    def create(cls, obj, body, evaldict, defaults=None,
               doc=None, module=None, addsource=True, add_args=(), **attrs):
        """
        Create a function from the strings name, signature and body.
        evaldict is the evaluation dictionary. If addsource is true an
        attribute __source__ is added to the result. The attributes attrs
        are added, if any.

        If add_args is not empty, these arguments will be prepended to the
        positional arguments.
        """
        if isinstance(obj, str):  # "name(signature)"
            name, rest = obj.strip().split('(', 1)
            signature = rest[:-1]  # strip a right parens
            func = None
        else:  # a function
            name = None
            signature = None
            func = obj
        self = cls(func, name, signature, defaults, doc, module)
        ibody = '\n'.join('    ' + line for line in body.splitlines())
        caller = evaldict.get('_call_')  # when called from `decorate`
        if caller and iscoroutinefunction(caller):
            body = ('async def %(name)s(%(signature)s):\n' + ibody).replace(
                'return', 'return await')
        else:
            body = 'def %(name)s(%(signature)s):\n' + ibody

        # Handle possible signature changes
        sig_modded = False
        if len(add_args) > 0:
            # prepend them as positional args - hence the reversed()
            for arg in reversed(add_args):
                if arg not in self.args:
                    self.args = [arg] + self.args
                    sig_modded = True
                else:
                    # the argument already exists in the wrapped
                    # function, nothing to do.
                    pass
        if sig_modded:
            self.refresh_signature()

        # make the function
        func = self.make(body, evaldict, addsource, **attrs)

        if sig_modded:
            # delete this annotation otherwise inspect.signature
            # will wrongly return the signature of func.__wrapped__
            # instead of the signature of func
            del func.__wrapped__

        return func


def _extract_additional_args(f_sig, add_args_names, args, kwargs):
    """
    Processes the arguments received by our caller so that at the end, args
    and kwargs only contain what is needed by f (according to f_sig). All
    additional arguments are returned separately, in order described by
    `add_args_names`. If some names in `add_args_names` are present in `f_sig`,
    then the arguments will appear both in the additional arguments and in
    *args, **kwargs.

    In the end, only *args can possibly be modified by the procedure (by removing
    from it all additional arguments that were not in f_sig and were prepended).

    So the result is a tuple (add_args, args)

    :return: a tuple (add_args, args) where `add_args` are the values of
        arguments named in `add_args_names` in the same order ; and `args` is
        the positional arguments to send to the wrapped function together with
        kwargs (args now only contains the positional args that are required by
        f, without the extra ones)
    """
    # -- first the 'truly' additional ones (the ones not in the signature)
    add_args = [None] * len(add_args_names)
    for i, arg_name in enumerate(add_args_names):
        if arg_name not in f_sig.parameters:
            # remove this argument from the args and put it in the right place
            add_args[i] = args[0]
            args = args[1:]

    # -- then the ones that already exist in the signature. Thanks,inspect pkg!
    bound = f_sig.bind(*args, **kwargs)
    for i, arg_name in enumerate(add_args_names):
        if arg_name in f_sig.parameters:
            add_args[i] = bound.arguments[arg_name]

    return add_args, args


def _wrap_caller_for_additional_args(func, caller, additional_args):
    """
    This internal function wraps the caller so as to handle all cases
    (if some additional args are already present in the signature or not)
    so as to ensure a consistent caller signature.

    :return: a new caller wrapping the caller, to be used in `decorate`
    """
    f_sig = signature(func)

    # We will create a caller above the original caller in order to check
    # if additional_args are already present in the signature or not, and
    # act accordingly
    original_caller = caller

    # -- then create the appropriate function signature according to
    # wrapped function signature assume that original_caller has all
    # additional args as first positional arguments, in order
    if not isgeneratorfunction(original_caller):
        def caller(f, *args, **kwargs):
            # Retrieve the values for additional args.
            add_args, args = _extract_additional_args(f_sig, additional_args,
                                                      args, kwargs)

            # Call the original caller
            return original_caller(f, *itertools.chain(add_args, args),
                                   **kwargs)
    else:
        def caller(f, *args, **kwargs):
            # Retrieve the value for additional args.
            add_args, args = _extract_additional_args(f_sig, additional_args,
                                                      args, kwargs)

            # Call the original caller
            for res in original_caller(f, *itertools.chain(add_args, args),
                                       **kwargs):
                yield res

    return caller


def decorate(func, caller, extras=(), additional_args=()):
    """
    decorate(func, caller) decorates a function using a caller.
    If the caller is a generator function, the resulting function
    will be a generator function.

    You can provide additional arguments with `additional_args`. In that case
    the caller's signature should be

        `caller(f, <additional_args_in_order>, *args, **kwargs)`.

    `*args, **kwargs` will always contain the arguments required by the inner
    function `f`. If `additional_args` contains argument names that are already
    present in `func`, they will be present both in <additional_args_in_order>
    AND in `*args, **kwargs` so that it remains easy for the `caller` both to
    get the additional arguments' values directly, and to call `f` with the
    right arguments.
    """
    if len(additional_args) > 0:
        # wrap the caller so as to handle all cases
        # (if some additional args are already present in the signature or not)
        # so as to ensure a consistent caller signature
        caller = _wrap_caller_for_additional_args(func, caller, additional_args)

    evaldict = dict(_call_=caller, _func_=func)
    es = ''
    for i, extra in enumerate(extras):
        ex = '_e%d_' % i
        evaldict[ex] = extra
        es += ex + ', '

    if '3.5' <= sys.version < '3.6':
        # with Python 3.5 isgeneratorfunction returns True for all coroutines
        # however we know that it is NOT possible to have a generator
        # coroutine in python 3.5: PEP525 was not there yet
        generatorcaller = isgeneratorfunction(
            caller) and not iscoroutinefunction(caller)
    else:
        generatorcaller = isgeneratorfunction(caller)
    if generatorcaller:
        fun = FunctionMaker.create(
            func, "for res in _call_(_func_, %s%%(shortsignature)s):\n"
                  "    yield res" % es, evaldict,
            add_args=additional_args, __wrapped__=func)
    else:
        fun = FunctionMaker.create(
            func, "return _call_(_func_, %s%%(shortsignature)s)" % es,
            evaldict, add_args=additional_args, __wrapped__=func)
    if hasattr(func, '__qualname__'):
        fun.__qualname__ = func.__qualname__
    return fun


def decorator(caller, _func=None):
    """decorator(caller) converts a caller function into a decorator"""
    if _func is not None:  # return a decorated function
        # this is obsolete behavior; you should use decorate instead
        return decorate(_func, caller)
    # else return a decorator function
    defaultargs, defaults = '', ()
    if inspect.isclass(caller):
        name = caller.__name__.lower()
        doc = 'decorator(%s) converts functions/generators into ' \
            'factories of %s objects' % (caller.__name__, caller.__name__)
    elif inspect.isfunction(caller):
        if caller.__name__ == '<lambda>':
            name = '_lambda_'
        else:
            name = caller.__name__
        doc = caller.__doc__
        nargs = caller.__code__.co_argcount
        ndefs = len(caller.__defaults__ or ())
        defaultargs = ', '.join(caller.__code__.co_varnames[nargs-ndefs:nargs])
        if defaultargs:
            defaultargs += ','
        defaults = caller.__defaults__
    else:  # assume caller is an object with a __call__ method
        name = caller.__class__.__name__.lower()
        doc = caller.__call__.__doc__
    evaldict = dict(_call=caller, _decorate_=decorate)
    dec = FunctionMaker.create(
        '%s(%s func)' % (name, defaultargs),
        'if func is None: return lambda func:  _decorate_(func, _call, (%s))\n'
        'return _decorate_(func, _call, (%s))' % (defaultargs, defaultargs),
        evaldict, doc=doc, module=caller.__module__, __wrapped__=caller)
    if defaults:
        dec.__defaults__ = defaults + (None,)
    return dec


# ####################### contextmanager ####################### #

try:  # Python >= 3.2
    from contextlib import _GeneratorContextManager
except ImportError:  # Python >= 2.5
    from contextlib import GeneratorContextManager as _GeneratorContextManager


class ContextManager(_GeneratorContextManager):
    def __call__(self, func):
        """Context manager decorator"""
        return FunctionMaker.create(
            func, "with _self_: return _func_(%(shortsignature)s)",
            dict(_self_=self, _func_=func), __wrapped__=func)


init = getfullargspec(_GeneratorContextManager.__init__)
n_args = len(init.args)
if n_args == 2 and not init.varargs:  # (self, genobj) Python 2.7
    def __init__(self, g, *a, **k):
        return _GeneratorContextManager.__init__(self, g(*a, **k))
    ContextManager.__init__ = __init__
elif n_args == 2 and init.varargs:  # (self, gen, *a, **k) Python 3.4
    pass
elif n_args == 4:  # (self, gen, args, kwds) Python 3.5
    def __init__(self, g, *a, **k):
        return _GeneratorContextManager.__init__(self, g, a, k)
    ContextManager.__init__ = __init__

_contextmanager = decorator(ContextManager)


def contextmanager(func):
    # Enable Pylint config: contextmanager-decorators=decorator.contextmanager
    return _contextmanager(func)


# ############################ dispatch_on ############################ #

def append(a, vancestors):
    """
    Append ``a`` to the list of the virtual ancestors, unless it is already
    included.
    """
    add = True
    for j, va in enumerate(vancestors):
        if issubclass(va, a):
            add = False
            break
        if issubclass(a, va):
            vancestors[j] = a
            add = False
    if add:
        vancestors.append(a)


# inspired from simplegeneric by P.J. Eby and functools.singledispatch
def dispatch_on(*dispatch_args):
    """
    Factory of decorators turning a function into a generic function
    dispatching on the given arguments.
    """
    assert dispatch_args, 'No dispatch args passed'
    dispatch_str = '(%s,)' % ', '.join(dispatch_args)

    def check(arguments, wrong=operator.ne, msg=''):
        """Make sure one passes the expected number of arguments"""
        if wrong(len(arguments), len(dispatch_args)):
            raise TypeError('Expected %d arguments, got %d%s' %
                            (len(dispatch_args), len(arguments), msg))

    def gen_func_dec(func):
        """Decorator turning a function into a generic function"""

        # first check the dispatch arguments
        argset = set(getfullargspec(func).args)
        if not set(dispatch_args) <= argset:
            raise NameError('Unknown dispatch arguments %s' % dispatch_str)

        typemap = {}

        def vancestors(*types):
            """
            Get a list of sets of virtual ancestors for the given types
            """
            check(types)
            ras = [[] for _ in range(len(dispatch_args))]
            for types_ in typemap:
                for t, type_, ra in zip(types, types_, ras):
                    if issubclass(t, type_) and type_ not in t.mro():
                        append(type_, ra)
            return [set(ra) for ra in ras]

        def ancestors(*types):
            """
            Get a list of virtual MROs, one for each type
            """
            check(types)
            lists = []
            for t, vas in zip(types, vancestors(*types)):
                n_vas = len(vas)
                if n_vas > 1:
                    raise RuntimeError(
                        'Ambiguous dispatch for %s: %s' % (t, vas))
                elif n_vas == 1:
                    va, = vas
                    mro = type('t', (t, va), {}).mro()[1:]
                else:
                    mro = t.mro()
                lists.append(mro[:-1])  # discard t and object
            return lists

        def register(*types):
            """
            Decorator to register an implementation for the given types
            """
            check(types)

            def dec(f):
                check(getfullargspec(f).args, operator.lt, ' in ' + f.__name__)
                typemap[types] = f
                return f
            return dec

        def dispatch_info(*types):
            """
            An utility to introspect the dispatch algorithm
            """
            check(types)
            lst = []
            for anc in itertools.product(*ancestors(*types)):
                lst.append(tuple(a.__name__ for a in anc))
            return lst

        def _dispatch(dispatch_args, *args, **kw):
            types = tuple(type(arg) for arg in dispatch_args)
            try:  # fast path
                f = typemap[types]
            except KeyError:
                pass
            else:
                return f(*args, **kw)
            combinations = itertools.product(*ancestors(*types))
            next(combinations)  # the first one has been already tried
            for types_ in combinations:
                f = typemap.get(types_)
                if f is not None:
                    return f(*args, **kw)

            # else call the default implementation
            return func(*args, **kw)

        return FunctionMaker.create(
            func, 'return _f_(%s, %%(shortsignature)s)' % dispatch_str,
            dict(_f_=_dispatch), register=register, default=func,
            typemap=typemap, vancestors=vancestors, ancestors=ancestors,
            dispatch_info=dispatch_info, __wrapped__=func)

    gen_func_dec.__name__ = 'dispatch_on' + dispatch_str
    return gen_func_dec
