from __future__ import absolute_import, division

import sys
from textwrap import dedent

import pytest
from IPython.lib.pretty import pretty

from represent import autorepr


def test_standard():
    @autorepr
    class A(object):
        def __init__(self):
            pass

    @autorepr
    class B(object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    assert repr(A()) == 'A()'
    assert pretty(A()) == 'A()'

    assert repr(B(1, 2)) == 'B(a=1, b=2, c=5)'
    assert pretty(B(1, 2)) == 'B(a=1, b=2, c=5)'


def test_positional():
    @autorepr(positional=1)
    class A(object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @autorepr(positional=2)
    class B(object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @autorepr(positional='a')
    class C(object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c

    @autorepr(positional=['a', 'b'])
    class D(object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c


    assert repr(A(1, 2)) == 'A(1, b=2, c=5)'
    assert pretty(A(1, 2)) == 'A(1, b=2, c=5)'

    assert repr(B(1, 2)) == 'B(1, 2, c=5)'
    assert pretty(B(1, 2)) == 'B(1, 2, c=5)'

    assert repr(C(1, 2)) == 'C(1, b=2, c=5)'
    assert pretty(C(1, 2)) == 'C(1, b=2, c=5)'

    assert repr(D(1, 2)) == 'D(1, 2, c=5)'
    assert pretty(D(1, 2)) == 'D(1, 2, c=5)'

    with pytest.raises(ValueError):
        @autorepr(positional='b')
        class E(object):
            def __init__(self, a, b):
                pass


@pytest.mark.skipif(sys.version_info < (3,), reason="Requires Python 3")
def test_kwonly():
    code = dedent("""
        with pytest.raises(ValueError):
            @autorepr(positional='a')
            class A:
                def __init__(self, *, a):
                    pass
    """)

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

    class B(object):
        def __init__(self):
            pass

    with pytest.raises(TypeError):
        autorepr(B, positional=1)


def test_cycle():
    @autorepr
    class A(object):
        def __init__(self, a=None):
            self.a = a

    a = A()
    a.a = a

    assert pretty(a) == 'A(a=A(...))'


def test_reuse():
    """autorepr was looking at classname to determine whether or not to add the
    methods, but this assumption isn't valid in some cases.
    """
    @autorepr
    class A(object):
        def __init__(self, a):
            self.a = a

    _A = A

    @autorepr
    class A(_A):
        def __init__(self, a, b):
            super(A, self).__init__(a=a)
            self.b = b

    a = A(1, 2)
    assert repr(a) == 'A(a=1, b=2)'
