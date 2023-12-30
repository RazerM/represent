import sys
from textwrap import dedent
from unittest.mock import Mock

import pytest
from IPython.lib.pretty import pretty

from represent import autorepr


def test_standard():
    @mock_repr_pretty
    @autorepr
    class A:
        def __init__(self):
            pass

    @mock_repr_pretty
    @autorepr
    class B:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    assert repr(A()) == "A()"
    assert pretty(A()) == "A()"
    assert A._repr_pretty_.called

    assert repr(B(1, 2)) == "B(a=1, b=2, c=5)"
    assert pretty(B(1, 2)) == "B(a=1, b=2, c=5)"
    assert B._repr_pretty_.called


def test_positional():
    @mock_repr_pretty
    @autorepr(positional=1)
    class A:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @mock_repr_pretty
    @autorepr(positional=2)
    class B:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @mock_repr_pretty
    @autorepr(positional="a")
    class C:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @mock_repr_pretty
    @autorepr(positional=["a", "b"])
    class D:
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    assert repr(A(1, 2)) == "A(1, b=2, c=5)"
    assert pretty(A(1, 2)) == "A(1, b=2, c=5)"
    assert A._repr_pretty_.called

    assert repr(B(1, 2)) == "B(1, 2, c=5)"
    assert pretty(B(1, 2)) == "B(1, 2, c=5)"
    assert B._repr_pretty_.called

    assert repr(C(1, 2)) == "C(1, b=2, c=5)"
    assert pretty(C(1, 2)) == "C(1, b=2, c=5)"
    assert C._repr_pretty_.called

    assert repr(D(1, 2)) == "D(1, 2, c=5)"
    assert pretty(D(1, 2)) == "D(1, 2, c=5)"
    assert D._repr_pretty_.called

    with pytest.raises(ValueError):

        @autorepr(positional="b")
        class E:
            def __init__(self, a, b):
                pass


@pytest.mark.skipif(sys.version_info < (3,), reason="Requires Python 3")
def test_kwonly():
    code = dedent(
        """
        with pytest.raises(ValueError):
            @autorepr(positional='a')
            class A:
                def __init__(self, *, a):
                    pass
    """
    )

    exec(code)


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
    @mock_repr_pretty
    @autorepr
    class A:
        def __init__(self, a=None):
            self.a = a

    a = A()
    a.a = a

    assert pretty(a) == "A(a=A(...))"
    assert A._repr_pretty_.call_count == 2


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


@pytest.mark.skipif(sys.version_info < (3, 2), reason="Requires Python 3.2+")
def test_recursive_repr():
    """Test that autorepr applies the :func:`reprlib.recursive_repr` decorator."""

    @mock_repr_pretty
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
    @mock_repr_pretty
    @autorepr(include_pretty=include_pretty)
    class A:
        def __init__(self, a):
            self.a = a

    a = A(1)
    reprstr = "A(a=1)"
    assert repr(a) == reprstr

    if include_pretty:
        assert pretty(a) == reprstr
        assert A._repr_pretty_.call_count == 1
    else:
        # check pretty falls back to __repr__ (to make sure we didn't leave a
        # broken _repr_pretty_ on the class)
        assert pretty(a) == reprstr
        assert not hasattr(A, "_repr_pretty_")


def mock_repr_pretty(cls):
    """Wrap cls._repr_pretty_ in a mock, if it exists."""
    _repr_pretty_ = getattr(cls, "_repr_pretty_", None)

    # Only mock it if it's there, it's up to the tests to check the mock was
    # called.
    if _repr_pretty_ is not None:
        cls._repr_pretty_ = Mock(wraps=_repr_pretty_)

    return cls
