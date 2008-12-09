##########################     LICENCE    ###############################
      
##   Redistributions of source code must retain the above copyright 
##   notice, this list of conditions and the following disclaimer.
##   Redistributions in bytecode form must reproduce the above copyright
##   notice, this list of conditions and the following disclaimer in
##   the documentation and/or other materials provided with the
##   distribution. 

##   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
##   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
##   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
##   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
##   HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
##   INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
##   BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
##   OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
##   TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
##   USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
##   DAMAGE.

"""
Decorator module, see http://pypi.python.org/pypi/decorator
for the documentation.
"""

## The basic trick is to generate the source code for the decorated function
## with the right signature and to evaluate it.

__all__ = ["decorator", "makefn", "getsignature", "upgrade_dec"]

import os, sys, re, inspect, warnings
from tempfile import mkstemp

DEF = re.compile('\s*def\s*([_\w][_\w\d]*)\s*\(')

def _callermodule(level=2):
    return sys._getframe(level).f_globals.get('__name__', '?')
 
def getsignature(func):
    "Return the signature of a function as a string"
    argspec = inspect.getargspec(func)
    return inspect.formatargspec(formatvalue=lambda val: "", *argspec)[1:-1]

class FuncData(object):
    def __init__(self, func=None, name=None, signature=None,
                 defaults=None, doc=None, module=None, funcdict=None):
        if func: # func can also be a class or a callable
            self.name = func.__name__
            self.doc = func.__doc__
            self.module = func.__module__
            if inspect.isfunction(func):
                self.signature = getsignature(func)
                self.defaults = func.func_defaults
                self.dict = func.__dict__
        if name:
            self.name = name
        if signature:
            self.signature = signature
        if defaults:
            self.defaults = defaults
        if doc:
            self.doc = doc
        if module:
            self.module = module
        if funcdict:
            self.dict = funcdict

    def update(self, func, **kw):
        func.__name__ = getattr(self, 'name', 'noname')
        func.__doc__ = getattr(self, 'doc', None)
        func.__dict__ = getattr(self, 'dict', {})
        func.func_defaults = getattr(self, 'defaults', None)
        func.__module__ = getattr(self, 'module', _callermodule())
        func.__dict__.update(kw)
        return func
    
    def __getitem__(self, name):
        return getattr(self, name)
    
def makefn(src, funcdata, save_source=True, **evaldict):
    src += os.linesep # add a newline just for safety
    name = DEF.match(src).group(1) # extract the function name from the source
    if save_source:
        fhandle, fname = mkstemp()
        os.write(fhandle, src)
        os.close(fhandle)
    else:
        fname = '?'
    code = compile(src, fname, 'single')
    exec code in evaldict
    func = evaldict[name]
    return funcdata.update(func, __source__=src)

def decorator_apply(caller, func):
    "decorator.apply(caller, func) is akin to decorator(caller)(func)"
    fd = FuncData(func)
    name = fd.name
    signature = fd.signature
    for arg in signature.split(','):
        argname = arg.strip(' *')
        assert not argname in('_func_', '_call_'), (
            '%s is a reserved argument name!' % argname)
    src = """def %(name)s(%(signature)s):
    return _call_(_func_, %(signature)s)""" % locals()
    return makefn(src, fd, save_source=False, _func_=func, _call_=caller)

def decorator(caller):
    """
    decorator(caller) converts a caller function into a decorator.
    """
    src = 'def %s(func): return appl(caller, func)' % caller.__name__
    return makefn(src, FuncData(caller), save_source=False,
                  caller=caller, appl=decorator_apply)

decorator.apply = decorator_apply

@decorator
def deprecated(func, *args, **kw):
    "A decorator for deprecated functions"
    warnings.warn('Calling the deprecated function %r' % func.__name__,
                  DeprecationWarning, stacklevel=3)
    return func(*args, **kw)

def upgrade_dec(dec):
    def new_dec(func):
        fd = FuncData(func)
        src = '''def %(name)s(%(signature)s):
        return decorated(%(signature)s)''' % fd
        return makefn(src, fd, save_source=False, decorated=dec(func))
    return FuncData(dec).update(new_dec)
