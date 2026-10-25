"""Wrapper introspection regressions and shared-helper compatibility."""

import functools
import inspect
import sys
import unittest
from typing import TYPE_CHECKING

from decorator import (
    FunctionMaker, decorate, decorator, decoratorx, dispatch_on,
    getfullargspec, inspect_sig,
)

if TYPE_CHECKING:
    class MissingInput:
        pass

    class MissingOption:
        pass

    class MissingResult:
        pass


class FullArgSpecTestCase(unittest.TestCase):
    def test_wraps_ignores_wrapped_signature(self):
        def original(hidden, count=2):
            return hidden, count

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        self.assertEqual(getfullargspec(wrapper), inspect.getfullargspec(wrapper))
        self.assertIs(wrapper.__wrapped__, original)

    def test_outer_parameters_and_defaults(self):
        def original(hidden):
            return hidden

        @functools.wraps(original)
        def wrapper(actual, optional=3, *items, flag=True, **options):
            return actual, optional, items, flag, options

        self.assertEqual(getfullargspec(wrapper), inspect.getfullargspec(wrapper))

    def test_stacked_wrappers(self):
        def original(hidden):
            return hidden

        @functools.wraps(original)
        def inner(middle, enabled=True):
            return original(middle)

        @functools.wraps(inner)
        def outer(actual, *, option=4):
            return inner(actual)

        self.assertEqual(getfullargspec(outer), inspect.getfullargspec(outer))
        self.assertIs(outer.__wrapped__, inner)
        self.assertIs(inner.__wrapped__, original)

    def test_cyclic_wrapper_chain(self):
        def wrapper(actual, *, flag=False):
            return actual, flag

        wrapper.__wrapped__ = wrapper
        try:
            actual = getfullargspec(wrapper)
        except ValueError as error:
            self.fail('getfullargspec followed a wrapper cycle: %s' % error)
        self.assertEqual(actual, inspect.getfullargspec(wrapper))
        self.assertIs(wrapper.__wrapped__, wrapper)

    def test_explicit_signature_precedes_wrapped(self):
        def original(hidden):
            return hidden

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        wrapper.__signature__ = inspect.Signature([
            inspect.Parameter('explicit', inspect.Parameter.POSITIONAL_ONLY,
                              default=7, annotation=int),
            inspect.Parameter('option', inspect.Parameter.KEYWORD_ONLY,
                              default=False, annotation=bool),
        ], return_annotation=str)
        self.assertEqual(getfullargspec(wrapper), inspect.getfullargspec(wrapper))
        self.assertEqual(getfullargspec(wrapper).args, ['explicit'])
        self.assertIs(inspect_sig(wrapper), wrapper.__signature__)

    def test_mixed_parameter_kinds_and_annotations(self):
        def ordinary(first: int, /, second: str = 'value', *items: float,
                     required: bool, optional: int = 4, **options: bytes) -> tuple:
            return first, second, items, required, optional, options

        self.assertEqual(getfullargspec(ordinary), inspect.getfullargspec(ordinary))
        self.assertEqual(getfullargspec(ordinary).annotations, {
            'first': int, 'second': str, 'items': float, 'required': bool,
            'optional': int, 'options': bytes, 'return': tuple,
        })

    def test_empty_defaults(self):
        def ordinary(value, *, required):
            return value, required

        actual = getfullargspec(ordinary)
        self.assertEqual(actual, inspect.getfullargspec(ordinary))
        self.assertIsNone(actual.defaults)
        self.assertIsNone(actual.kwonlydefaults)
        self.assertEqual(actual.annotations, {})

    def test_partial_is_unchanged(self):
        def ordinary(first, second=2, *, option=3):
            return first, second, option

        partial = functools.partial(ordinary, 1, option=4)
        before = partial.__dict__.copy(), partial.args, partial.keywords.copy()
        self.assertEqual(getfullargspec(partial), inspect.getfullargspec(partial))
        self.assertEqual((partial.__dict__, partial.args, partial.keywords), before)
        self.assertEqual(partial(), (1, 2, 4))

    def test_future_string_annotations(self):
        namespace = {}
        exec('from __future__ import annotations\n'
             'def ordinary(value: MissingInput, *, option: MissingOption = None) -> MissingResult:\n'
             '    return value\n', namespace)
        ordinary = namespace['ordinary']
        self.assertEqual(getfullargspec(ordinary), inspect.getfullargspec(ordinary))
        self.assertEqual(getfullargspec(ordinary).annotations, {
            'value': 'MissingInput', 'option': 'MissingOption', 'return': 'MissingResult',
        })

    @unittest.skipUnless(sys.version_info >= (3, 14), 'requires deferred annotations')
    def test_outer_deferred_annotations(self):
        from annotationlib import ForwardRef

        def original(hidden):
            return hidden

        def wrapper(actual: MissingInput, *, option: MissingOption = None) -> MissingResult:
            return original(actual)

        wrapper.__wrapped__ = original
        actual = getfullargspec(wrapper)
        self.assertEqual(actual.args, ['actual'])
        self.assertEqual(actual.kwonlyargs, ['option'])
        self.assertEqual(actual.kwonlydefaults, {'option': None})
        self.assertEqual(set(actual.annotations), {'actual', 'option', 'return'})
        for name, expected in (('actual', 'MissingInput'), ('option', 'MissingOption'),
                               ('return', 'MissingResult')):
            with self.subTest(annotation=name):
                self.assertIsInstance(actual.annotations[name], ForwardRef)
                self.assertEqual(actual.annotations[name].__forward_arg__, expected)


class InspectionConsumerTestCase(unittest.TestCase):
    def test_inspect_sig_follows_wrapped_by_default(self):
        def original(hidden, count=2):
            return hidden, count

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        self.assertEqual(inspect_sig(wrapper), inspect.signature(original))

    def test_inspect_sig_keyword_only_opt_out(self):
        option = inspect.signature(inspect_sig).parameters.get('follow_wrapped')
        self.assertIsNotNone(option)
        self.assertEqual(option.kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertIs(option.default, True)

        def original(hidden):
            return hidden

        @functools.wraps(original)
        def wrapper(actual, *, option=4):
            return original(actual)

        self.assertEqual(inspect_sig(wrapper, follow_wrapped=False),
                         inspect.signature(wrapper, follow_wrapped=False))

    @unittest.skipUnless(sys.version_info >= (3, 14), 'requires deferred annotations')
    def test_inspect_sig_preserves_forward_references(self):
        from annotationlib import ForwardRef

        def original(hidden: MissingInput) -> MissingResult:
            return hidden

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        signature = inspect_sig(wrapper)
        self.assertEqual(list(signature.parameters), ['hidden'])
        self.assertIsInstance(signature.parameters['hidden'].annotation, ForwardRef)
        self.assertEqual(signature.parameters['hidden'].annotation.__forward_arg__, 'MissingInput')
        self.assertIsInstance(signature.return_annotation, ForwardRef)
        self.assertEqual(signature.return_annotation.__forward_arg__, 'MissingResult')

    def test_decorate_preserves_binding_and_metadata(self):
        calls = []

        def original(value, count=2):
            """An ordinary target."""
            return value + count

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        def caller(func, *args, **kwargs):
            calls.append((func, args, kwargs))
            return func(*args, **kwargs)

        wrapped = decorate(wrapper, caller)
        self.assertEqual(wrapped(value=3), 5)
        self.assertEqual(calls, [(wrapper, (3, 2), {})])
        self.assertEqual(inspect.signature(wrapped), inspect.signature(original))
        self.assertEqual((wrapped.__name__, wrapped.__qualname__, wrapped.__doc__, wrapped.__module__),
                         (wrapper.__name__, wrapper.__qualname__, wrapper.__doc__, wrapper.__module__))
        self.assertIs(wrapped.__wrapped__, wrapper)
        self.assertIs(wrapped.__wrapped__.__wrapped__, original)
        with self.assertRaises(TypeError):
            wrapped(unknown=3)

    def test_decorate_preserves_keyword_syntax(self):
        calls = []

        def original(value, count=2):
            return value + count

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            return original(*args, **kwargs)

        def caller(func, *args, **kwargs):
            calls.append((args, kwargs))
            return func(*args, **kwargs)

        wrapped = decorate(wrapper, caller, kwsyntax=True)
        self.assertEqual(wrapped(value=3), 5)
        self.assertEqual(calls, [((), {'value': 3})])

    def test_decorator_preserves_wrapped_factory(self):
        def caller(func, increment=2, *args, **kwargs):
            return func(*args, **kwargs) + increment

        @functools.wraps(caller)
        def wrapped_caller(*args, **kwargs):
            return caller(*args, **kwargs)

        def ordinary(value=1):
            return value

        factory = decorator(wrapped_caller)
        self.assertIs(factory.__wrapped__, wrapped_caller)
        self.assertIs(factory.__wrapped__.__wrapped__, caller)
        self.assertEqual(factory(ordinary)(), 3)
        self.assertEqual(factory(increment=4)(ordinary)(value=3), 7)
        self.assertEqual(inspect.signature(factory), inspect.Signature([
            inspect.Parameter('func', inspect.Parameter.POSITIONAL_OR_KEYWORD),
            inspect.Parameter('increment', inspect.Parameter.POSITIONAL_OR_KEYWORD, default=2),
        ]))

    def test_function_maker_uses_outer_signature(self):
        def original(hidden):
            return hidden

        @functools.wraps(original)
        def wrapper(actual, optional=3, *items, flag=True, **options):
            return actual, optional, items, flag, options

        maker = FunctionMaker(wrapper)
        self.assertEqual(maker.args, ['actual', 'optional'])
        self.assertEqual(maker.defaults, (3,))
        self.assertEqual(maker.kwonlyargs, ['flag'])
        generated = FunctionMaker.create(wrapper, 'return _func_(%(shortsignature)s)', {'_func_': wrapper})
        self.assertEqual(inspect.signature(generated, follow_wrapped=False),
                         inspect.signature(wrapper, follow_wrapped=False))
        self.assertEqual(generated(2), (2, 3, (), True, {}))
        self.assertEqual(generated(2, 4, 5, flag=False, extra=6), (2, 4, (5,), False, {'extra': 6}))

    def test_function_maker_ordinary_function(self):
        def ordinary(value, count=2, *, option=3):
            return value, count, option

        generated = FunctionMaker.create(ordinary, 'return _func_(%(shortsignature)s)', {'_func_': ordinary})
        self.assertEqual(inspect.signature(generated), inspect.signature(ordinary))
        self.assertEqual(generated(1), (1, 2, 3))
        self.assertEqual(generated(1, option=4), (1, 2, 4))

    def test_decoratorx_uses_outer_signature(self):
        def original(hidden):
            return hidden

        @functools.wraps(original)
        def wrapper(actual, optional=3):
            return original(actual + optional)

        def caller(func, *args, **kwargs):
            return func(*args, **kwargs) * 2

        wrapped = decoratorx(caller)(wrapper)
        self.assertEqual(wrapped.__code__.co_varnames[:wrapped.__code__.co_argcount], ('actual', 'optional'))
        self.assertEqual(inspect.signature(wrapped, follow_wrapped=False),
                         inspect.signature(wrapper, follow_wrapped=False))
        self.assertEqual(wrapped(actual=2), 10)
        self.assertIs(wrapped.__wrapped__, wrapper)

    def test_decoratorx_ordinary_function(self):
        def ordinary(value=2):
            return value

        def caller(func, *args, **kwargs):
            return func(*args, **kwargs) + 1

        wrapped = decoratorx(caller)(ordinary)
        self.assertEqual(wrapped(), 3)
        self.assertEqual(wrapped(value=4), 5)
        self.assertEqual(inspect.signature(wrapped), inspect.signature(ordinary))

    def test_dispatch_on_uses_outer_parameter(self):
        def original(hidden):
            return 'base'

        @functools.wraps(original)
        def wrapper(actual):
            return original(actual)

        try:
            generic = dispatch_on('actual')(wrapper)
        except NameError as error:
            self.fail('dispatch_on rejected the actual wrapper parameter: %s' % error)

        @generic.register(int)
        def integer(actual):
            return 'integer'

        self.assertEqual(generic(1), 'integer')
        self.assertEqual(generic('value'), 'base')
        self.assertIs(generic.default, wrapper)

    def test_dispatch_on_ordinary_function(self):
        @dispatch_on('value')
        def ordinary(value):
            return 'base'

        @ordinary.register(int)
        def integer(value):
            return 'integer'

        self.assertEqual(ordinary(1), 'integer')
        self.assertEqual(ordinary('value'), 'base')


if __name__ == '__main__':
    unittest.main()
