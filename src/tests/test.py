from __future__ import absolute_import
import sys
import doctest
import unittest
import decimal
import inspect
import collections
from decorator import dispatch_on, contextmanager
try:
    from . import documentation
except (SystemError, ValueError):
    import documentation


@contextmanager
def assertRaises(etype):
    """This works in Python 2.6 too"""
    try:
        yield
    except etype:
        pass
    else:
        raise Exception('Expected %s' % etype)


class DocumentationTestCase(unittest.TestCase):
    def test(self):
        err = doctest.testmod(documentation)[0]
        self.assertEqual(err, 0)


class ExtraTestCase(unittest.TestCase):
    def test_signature(self):
        if hasattr(inspect, 'signature'):
            sig = inspect.signature(documentation.f1)
            self.assertEqual(str(sig), '(x)')

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

        class A(object):
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
            return "int %s" % (i,)
        self.assertEqual(g(""), "base")
        self.assertEqual(g(12), "int 12")

    def test_register_error(self):
        @singledispatch
        def g(obj):
            return "base"

        with assertRaises(TypeError):
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
        c = collections
        d = {"a": "b"}
        l = [1, 2, 3]
        s = set([object(), None])
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

        if hasattr(c, 'ChainMap'):
            g.register(c.ChainMap)(lambda obj: "chainmap")
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
        if hasattr(c, 'ChainMap'):
            self.assertEqual(
                [abc.__name__ for abc in g.vancestors[0]],
                ['ChainMap', 'MutableMapping', 'MutableSequence', 'MutableSet',
                 'Mapping', 'Sequence', 'Set', 'Sized'])
        else:
            self.assertEqual(
                [abc.__name__ for abc in g.vancestors[0]],
                ['MutableMapping', 'MutableSequence', 'MutableSet',
                 'Mapping', 'Sequence', 'Set', 'Sized'])

    def test_mro_conflicts(self):
        c = collections

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
        self.assertEqual(g(o), "sized")   # because it's explicitly in __mro__
        c.Container.register(O)
        self.assertEqual(g(o), "sized")   # see above: Sized is in __mro__
        c.Set.register(O)
        self.assertEqual(g(o), "sized")
        # could be set because c.Set is a subclass of
        # c.Sized and c.Container

        class P(object):
            pass
        p = P()
        self.assertEqual(g(p), "base")
        c.Iterable.register(P)
        self.assertEqual(g(p), "iterable")
        c.Container.register(P)

        with assertRaises(RuntimeError):
            g(p)

        class Q(c.Sized):
            def __len__(self):
                return 0
        q = Q()
        self.assertEqual(g(q), "sized")
        c.Iterable.register(Q)
        self.assertEqual(g(q), "sized")   # because it's explicitly in __mro__
        c.Set.register(Q)
        self.assertEqual(g(q), "sized")
        # could be because c.Set is a subclass of
        # c.Sized and c.Iterable

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
            h(c.defaultdict(lambda: 0))

        class R(c.defaultdict):
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
        with assertRaises(RuntimeError):  # not for standardlib
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
        if sys.version >= '3':
            self.assertEqual(h(u), "sized")
            # implicit Sized subclass inferred
            # from the existence of __len__()

        c.Container.register(U)
        # There is no preference for registered versus inferred ABCs.
        with assertRaises(RuntimeError):
            h(u)

        class V(c.Sized, S):
            def __len__(self):
                return 0

        @singledispatch
        def j(obj):
            return "base"

        @j.register(S)
        def j_s(arg):
            return "s"

        @j.register(c.Container)
        def j_container(arg):
            return "container"
        v = V()
        self.assertEqual(j(v), "s")
        c.Container.register(V)
        self.assertEqual(j(v), "s")  # could be "container"
        # because it ends up right after
        # Sized in the MRO

if __name__ == '__main__':
    unittest.main()
