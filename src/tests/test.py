import sys
import doctest
import unittest
import decimal
import inspect
import functools
import asyncio
from collections import defaultdict, ChainMap, abc as c
from decorator import dispatch_on, contextmanager, decorator
try:
    from . import documentation as doc  # good with pytest
except ImportError:
    import documentation as doc  # good with `python src/tests/test.py`


@contextmanager
def assertRaises(etype):
    """This works in Python 2.6 too"""
    try:
        yield
    except etype:
        pass
    else:
        raise Exception('Expected %s' % etype.__name__)


@decorator
async def before_after(coro, *args, **kwargs):
    return "<before>" + (await coro(*args, **kwargs)) + "<after>"


@decorator
def coro_to_func(coro, *args, **kw):
    return asyncio.run(coro(*args, **kw))


class CoroutineTestCase(unittest.TestCase):
    def test_before_after(self):
        @before_after
        async def coro(x):
            return x
        self.assertTrue(inspect.iscoroutinefunction(coro))
        out = asyncio.run(coro('x'))
        self.assertEqual(out, '<before>x<after>')

    def test_coro_to_func(self):
        @coro_to_func
        async def coro(x):
            return x
        self.assertFalse(inspect.iscoroutinefunction(coro))
        self.assertEqual(coro('x'), 'x')


def gen123():
    yield 1
    yield 2
    yield 3


class GeneratorCallerTestCase(unittest.TestCase):
    def test_gen123(self):
        @decorator
        def square(func, *args, **kw):
            for x in gen123():
                yield x * x
        new = square(gen123)
        self.assertTrue(inspect.isgeneratorfunction(new))
        self.assertEqual(list(new()), [1, 4, 9])


class DocumentationTestCase(unittest.TestCase):
    def test(self):
        err = doctest.testmod(doc)[0]
        self.assertEqual(err, 0)

    def test_copy_dunder_attrs(self):
        traced = doc.trace(doc.foo)
        self.assertIn('documentation', traced.__module__)
        self.assertEqual(traced.__annotations__, {})
        self.assertEqual(traced.__defaults__, (None,))

    def test_singledispatch1(self):
        with assertRaises(RuntimeError):
            doc.singledispatch_example1()

    def test_singledispatch2(self):
        doc.singledispatch_example2()

    def test_context_manager(self):

        @contextmanager
        def before_after(before, after):
            print(before)
            yield
            print(after)

        @before_after('BEFORE', 'AFTER')
        def hello_user(user):
            print('hello %s' % user)

        argspec = inspect.getfullargspec(hello_user)
        self.assertEqual(argspec.args, ['user'])


class ExtraTestCase(unittest.TestCase):
    def test_qualname(self):
        self.assertEqual(doc.operation1.__qualname__, 'operation1')

    def test_signature(self):
        sig = inspect.signature(doc.f1)
        self.assertEqual(str(sig), '(x)')

    def test_unique_filenames(self):
        @decorator
        def d1(f, *args, **kwargs):
            return f(*args, **kwargs)

        @decorator
        def d2(f, *args, **kwargs):
            return f(*args, **kwargs)

        @d1
        def f1(x, y, z):
            pass

        @d2
        def f2(x, y, z):
            pass

        f1_orig = f1

        @d1
        def f1(x, y, z):
            pass

        self.assertEqual(d1.__code__.co_filename,
                         d2.__code__.co_filename)
        self.assertEqual(f1.__code__.co_filename,
                         f2.__code__.co_filename)
        self.assertEqual(f1_orig.__code__.co_filename,
                         f1.__code__.co_filename)

    def test_no_first_arg(self):
        @decorator
        def example(*args, **kw):
            return args[0](*args[1:], **kw)

        @example
        def func(**kw):
            "Docstring"
            return kw

        # there is no confusion when passing args as a keyword argument
        self.assertEqual(func(args='a'), {'args': 'a'})
        self.assertEqual(func.__doc__, "Docstring")

    def test_decorator_factory(self):
        # similar to what IPython is doing in traitlets.config.application
        @decorator
        def catch_config_error(method, app, *args, **kwargs):
            return method(app)
        catch_config_error(lambda app, **kw: None)(1)

    def test_add1(self):
        # similar to what IPython is doing in traitlets.config.application
        @decorator
        def add(func, const=1, *args, **kwargs):
            return const + func(*args, **kwargs)

        def f(x):
            return x
        self.assertEqual(add(f, 2)(0), 2)

    def test_dan_schult(self):
        # see https://github.com/micheles/decorator/issues/120
        @decorator
        def prnt(func, index=0, *args, **kw):
            print(args[index])
            return func(*args, **kw)

        @prnt(index=2)  # print the value of the third argument
        def f(a, b, c=None):
            return [a, b, c]

        self.assertEqual(f(0, 1), [0, 1, None])

    def test_slow_wrapper(self):
        # see https://github.com/micheles/decorator/issues/123
        dd = defaultdict(list)
        doc.trace(defaultdict.__setitem__)(dd, 'x', [1])
        self.assertEqual(dd['x'], [1])
        doc.trace(defaultdict.__delitem__)(dd, 'x')
        self.assertEqual(dd['x'], [])
        # NB: defaultdict.__getitem__ has no signature and cannot be
        # decorated in CPython, while it is regular in PyPy


# ################### test dispatch_on ############################# #
# adapted from test_functools in Python 3.5
singledispatch = dispatch_on('obj')


class TestSingleDispatch(unittest.TestCase):
    def test_simple_overloads(self):
        @singledispatch
        def g(obj):
            return "base"

        @g.register(int)
        def g_int(i):
            return "integer"

        self.assertEqual(g("str"), "base")
        self.assertEqual(g(1), "integer")
        self.assertEqual(g([1, 2, 3]), "base")

    def test_mro(self):
        @singledispatch
        def g(obj):
            return "base"

        class A:
            pass

        class C(A):
            pass

        class B(A):
            pass

        class D(C, B):
            pass

        @g.register(A)
        def g_A(a):
            return "A"

        @g.register(B)
        def g_B(b):
            return "B"

        self.assertEqual(g(A()), "A")
        self.assertEqual(g(B()), "B")
        self.assertEqual(g(C()), "A")
        self.assertEqual(g(D()), "B")

    def test_register_decorator(self):
        @singledispatch
        def g(obj):
            return "base"

        @g.register(int)
        def g_int(i):
            return "int {}".format(i)
        self.assertEqual(g(""), "base")
        self.assertEqual(g(12), "int 12")

    def test_register_error(self):
        @singledispatch
        def g(obj):
            return "base"

        with assertRaises(TypeError):
            # wrong number of arguments
            @g.register(int)
            def g_int():
                return "int"

    def test_wrapping_attributes(self):
        @singledispatch
        def g(obj):
            "Simple test"
            return "Test"
        self.assertEqual(g.__name__, "g")
        if sys.flags.optimize < 2:
            self.assertEqual(g.__doc__, "Simple test")

    def test_c_classes(self):
        @singledispatch
        def g(obj):
            return "base"

        @g.register(decimal.DecimalException)
        def _(obj):
            return obj.args
        subn = decimal.Subnormal("Exponent < Emin")
        rnd = decimal.Rounded("Number got rounded")
        self.assertEqual(g(subn), ("Exponent < Emin",))
        self.assertEqual(g(rnd), ("Number got rounded",))

        @g.register(decimal.Subnormal)
        def _g(obj):
            return "Too small to care."
        self.assertEqual(g(subn), "Too small to care.")
        self.assertEqual(g(rnd), ("Number got rounded",))

    def test_register_abc(self):
        d = {"a": "b"}
        l = [1, 2, 3]
        s = {object(), None}
        f = frozenset(s)
        t = (1, 2, 3)

        @singledispatch
        def g(obj):
            return "base"

        self.assertEqual(g(d), "base")
        self.assertEqual(g(l), "base")
        self.assertEqual(g(s), "base")
        self.assertEqual(g(f), "base")
        self.assertEqual(g(t), "base")

        g.register(c.Sized)(lambda obj: "sized")
        self.assertEqual(g(d), "sized")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.MutableMapping)(lambda obj: "mutablemapping")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(ChainMap)(lambda obj: "chainmap")
        # irrelevant ABCs registered
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "sized")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.MutableSequence)(lambda obj: "mutablesequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "sized")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.MutableSet)(lambda obj: "mutableset")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.Mapping)(lambda obj: "mapping")
        self.assertEqual(g(d), "mutablemapping")  # not specific enough
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sized")

        g.register(c.Sequence)(lambda obj: "sequence")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "sized")
        self.assertEqual(g(t), "sequence")

        g.register(c.Set)(lambda obj: "set")
        self.assertEqual(g(d), "mutablemapping")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(dict)(lambda obj: "dict")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "mutablesequence")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(list)(lambda obj: "list")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "mutableset")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(set)(lambda obj: "concrete-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "set")
        self.assertEqual(g(t), "sequence")

        g.register(frozenset)(lambda obj: "frozen-set")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "sequence")

        g.register(tuple)(lambda obj: "tuple")
        self.assertEqual(g(d), "dict")
        self.assertEqual(g(l), "list")
        self.assertEqual(g(s), "concrete-set")
        self.assertEqual(g(f), "frozen-set")
        self.assertEqual(g(t), "tuple")

    def test_mro_conflicts(self):
        @singledispatch
        def g(obj):
            return "base"

        class O(c.Sized):
            def __len__(self):
                return 0
        o = O()
        self.assertEqual(g(o), "base")
        g.register(c.Iterable)(lambda arg: "iterable")
        g.register(c.Container)(lambda arg: "container")
        g.register(c.Sized)(lambda arg: "sized")
        g.register(c.Set)(lambda arg: "set")
        self.assertEqual(g(o), "sized")
        c.Iterable.register(O)
        self.assertEqual(g(o), "sized")
        c.Container.register(O)
        with assertRaises(RuntimeError):  # was "sized" because in mro
            self.assertEqual(g(o), "sized")
        c.Set.register(O)
        self.assertEqual(g(o), "set")

        class P:
            pass
        p = P()
        self.assertEqual(g(p), "base")
        c.Iterable.register(P)
        self.assertEqual(g(p), "iterable")
        c.Container.register(P)

        with assertRaises(RuntimeError):
            self.assertEqual(g(p), "iterable")

        class Q(c.Sized):
            def __len__(self):
                return 0
        q = Q()
        self.assertEqual(g(q), "sized")
        c.Iterable.register(Q)
        self.assertEqual(g(q), "sized")
        c.Set.register(Q)
        self.assertEqual(g(q), "set")
        # because c.Set is a subclass of c.Sized and c.Iterable

        @singledispatch
        def h(obj):
            return "base"

        @h.register(c.Sized)
        def h_sized(arg):
            return "sized"

        @h.register(c.Container)
        def h_container(arg):
            return "container"
        # Even though Sized and Container are explicit bases of MutableMapping,
        # this ABC is implicitly registered on defaultdict which makes all of
        # MutableMapping's bases implicit as well from defaultdict's
        # perspective.
        with assertRaises(RuntimeError):
            self.assertEqual(h(defaultdict(int)), "sized")

        class R(defaultdict):
            pass
        c.MutableSequence.register(R)

        @singledispatch
        def i(obj):
            return "base"

        @i.register(c.MutableMapping)
        def i_mapping(arg):
            return "mapping"

        @i.register(c.MutableSequence)
        def i_sequence(arg):
            return "sequence"
        r = R()
        with assertRaises(RuntimeError):  # was no error
            self.assertEqual(i(r), "sequence")

        class S:
            pass

        class T(S, c.Sized):
            def __len__(self):
                return 0
        t = T()
        self.assertEqual(h(t), "sized")
        c.Container.register(T)
        self.assertEqual(h(t), "sized")   # because it's explicitly in the MRO

        class U:
            def __len__(self):
                return 0
        u = U()
        self.assertEqual(h(u), "sized")
        # implicit Sized subclass inferred
        # from the existence of __len__()

        c.Container.register(U)
        # There is no preference for registered versus inferred ABCs.
        with assertRaises(RuntimeError):
            h(u)


@decorator
def partial_before_after(func, *args, **kwargs):
    return "<before>" + func(*args, **kwargs) + "<after>"


class PartialTestCase(unittest.TestCase):
    def test_before_after(self):
        def origin_func(x, y):
            return x + y
        _func = functools.partial(origin_func, "x")
        partial_func = partial_before_after(_func)
        out = partial_func("y")
        self.assertEqual(out, '<before>xy<after>')


if __name__ == '__main__':
    unittest.main()
