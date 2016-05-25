from __future__ import absolute_import, division

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
            def __init__(self, a, b, c=5):
                self.a = a
                self.b = b
                self.c = c
