from contextlib import contextmanager
from functools import partial
from textwrap import dedent
from types import MethodType
from unittest.mock import Mock, patch

import pytest
from IPython.lib.pretty import pretty
from rich.pretty import pretty_repr

from represent import autorepr


class WrappedMethod:
    def __init__(self, method):
        self.mock = Mock(method, wraps=method)

    def __get__(self, instance, owner):
        if instance is None:
            return self.mock
        return partial(self.mock, instance)


@contextmanager
def spy_on_method(target, attribute):
    wrapped = WrappedMethod(getattr(target, attribute))
    with patch.object(target, attribute, wrapped):
        yield wrapped.mock


def test_standard():
    @autorepr
    class A:
        def __init__(self):
            pass

    @autorepr
    class B:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    assert repr(A()) == "A()"

    with spy_on_method(A, "_repr_pretty_"):
        assert pretty(A()) == "A()"
        assert A._repr_pretty_.called

    with spy_on_method(A, "__rich_repr__"):
        assert pretty_repr(A()) == "A()"
        assert A.__rich_repr__.called

    assert repr(B(1, 2)) == "B(a=1, b=2, c=5)"

    with spy_on_method(B, "_repr_pretty_"):
        assert pretty(B(1, 2)) == "B(a=1, b=2, c=5)"
        assert B._repr_pretty_.called

    with spy_on_method(B, "__rich_repr__"):
        assert pretty_repr(B(1, 2)) == "B(a=1, b=2, c=5)"
        assert B.__rich_repr__.called


def test_positional():
    @autorepr(positional=1)
    class A:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @autorepr(positional=2)
    class B:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @autorepr(positional="a")
    class C:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @autorepr(positional=["a", "b"])
    class D:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    assert repr(A(1, 2)) == "A(1, b=2, c=5)"

    with spy_on_method(A, "_repr_pretty_"):
        assert pretty(A(1, 2)) == "A(1, b=2, c=5)"
        assert A._repr_pretty_.called

    with spy_on_method(A, "__rich_repr__"):
        assert pretty_repr(A(1, 2)) == "A(1, b=2, c=5)"
        assert A.__rich_repr__.called

    assert repr(B(1, 2)) == "B(1, 2, c=5)"

    with spy_on_method(B, "_repr_pretty_"):
        assert pretty(B(1, 2)) == "B(1, 2, c=5)"
        assert B._repr_pretty_.called

    with spy_on_method(B, "__rich_repr__"):
        assert pretty_repr(B(1, 2)) == "B(1, 2, c=5)"
        assert B.__rich_repr__.called

    assert repr(C(1, 2)) == "C(1, b=2, c=5)"

    with spy_on_method(C, "_repr_pretty_"):
        assert pretty(C(1, 2)) == "C(1, b=2, c=5)"
        assert C._repr_pretty_.called

    with spy_on_method(C, "__rich_repr__"):
        assert pretty_repr(C(1, 2)) == "C(1, b=2, c=5)"
        assert C.__rich_repr__.called

    assert repr(D(1, 2)) == "D(1, 2, c=5)"

    with spy_on_method(D, "_repr_pretty_"):
        assert pretty(D(1, 2)) == "D(1, 2, c=5)"
        assert D._repr_pretty_.called

    with spy_on_method(D, "__rich_repr__"):
        assert pretty_repr(D(1, 2)) == "D(1, 2, c=5)"
        assert D.__rich_repr__.called

    with pytest.raises(ValueError):

        @autorepr(positional="b")
        class E:
            def __init__(self, a, b):
                pass


def test_kwonly():
    with pytest.raises(ValueError):

        @autorepr(positional="a")
        class A:
            def __init__(self, *, a):
                pass


def test_exceptions():
    with pytest.raises(TypeError):
        autorepr(1)

    with pytest.raises(TypeError):
        autorepr(1, 2)

    with pytest.raises(TypeError):
        autorepr(wrongkeyword=True)

    with pytest.raises(TypeError):
        autorepr()

    class B:
        def __init__(self):
            pass

    with pytest.raises(TypeError):
        autorepr(B, positional=1)


def test_cycle():
    @autorepr
    class A:
        def __init__(self, a=None):
            self.a = a

    a = A()
    a.a = a

    assert repr(a) == "A(a=...)"

    with spy_on_method(A, "_repr_pretty_"):
        assert pretty(a) == "A(a=A(...))"
        assert A._repr_pretty_.call_count == 2

    with spy_on_method(A, "__rich_repr__"):
        assert pretty_repr(a) == "A(a=...)"
        assert A.__rich_repr__.call_count == 1


def test_reuse():
    """autorepr was looking at classname to determine whether or not to add the
    methods, but this assumption isn't valid in some cases.
    """

    @autorepr
    class A:
        def __init__(self, a):
            self.a = a

    _A = A

    @autorepr
    class A(_A):
        def __init__(self, a, b):
            super().__init__(a=a)
            self.b = b

    a = A(1, 2)
    assert repr(a) == "A(a=1, b=2)"


def test_recursive_repr():
    """Test that autorepr applies the :func:`reprlib.recursive_repr` decorator."""

    @autorepr
    class A:
        def __init__(self, a=None):
            self.a = a

    a = A()
    a.a = a

    reprstr = "A(a=...)"
    assert repr(a) == reprstr


@pytest.mark.parametrize("include_pretty", [False, True])
def test_include_pretty(include_pretty):
    @autorepr(include_pretty=include_pretty)
    class A:
        def __init__(self, a):
            self.a = a

    a = A(1)
    reprstr = "A(a=1)"
    assert repr(a) == reprstr

    if include_pretty:
        with spy_on_method(A, "_repr_pretty_"):
            assert pretty(a) == reprstr
            assert A._repr_pretty_.call_count == 1
    else:
        # check pretty falls back to __repr__ (to make sure we didn't leave a
        # broken _repr_pretty_ on the class)
        assert pretty(a) == reprstr
        assert not hasattr(A, "_repr_pretty_")


@pytest.mark.parametrize("include_rich", [False, True])
def test_include_rich(include_rich):
    @autorepr(include_rich=include_rich)
    class A:
        def __init__(self, a):
            self.a = a

    a = A(1)
    reprstr = "A(a=1)"
    assert repr(a) == reprstr

    if include_rich:
        with spy_on_method(A, "__rich_repr__"):
            assert pretty_repr(a) == reprstr
            assert A.__rich_repr__.call_count == 1
    else:
        # check rich falls back to __repr__ (to make sure we didn't leave a
        # broken _repr_pretty_ on the class)
        assert pretty_repr(a) == reprstr
        assert not hasattr(A, "__rich_repr__")
