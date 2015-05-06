from __future__ import absolute_import, division

import pytest
from IPython.lib.pretty import pprint, pretty

from represent import ReprMixin


def test_standard():
    class A(ReprMixin, object):
        def __init__(self):
            super(A, self).__init__()

    class B(ReprMixin, object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c
            super(B, self).__init__()

    assert repr(A()) == 'A()'
    assert pretty(A()) == 'A()'

    assert repr(B(1, 2)) == 'B(a=1, b=2, c=5)'
    assert pretty(B(1, 2)) == 'B(a=1, b=2, c=5)'


def test_positional():
    class A(ReprMixin, object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c
            super(A, self).__init__(positional=1)

    class B(ReprMixin, object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c
            super(B, self).__init__(positional=2)

    class C(ReprMixin, object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c
            super(C, self).__init__(positional='a')

    class D(ReprMixin, object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c
            super(D, self).__init__(positional=['a', 'b'])

    assert repr(A(1, 2)) == 'A(1, b=2, c=5)'
    assert pretty(A(1, 2)) == 'A(1, b=2, c=5)'

    assert repr(B(1, 2)) == 'B(1, 2, c=5)'
    assert pretty(B(1, 2)) == 'B(1, 2, c=5)'

    assert repr(C(1, 2)) == 'C(1, b=2, c=5)'
    assert pretty(C(1, 2)) == 'C(1, b=2, c=5)'

    assert repr(D(1, 2)) == 'D(1, 2, c=5)'
    assert pretty(D(1, 2)) == 'D(1, 2, c=5)'

    class E(ReprMixin, object):
        def __init__(self, a, b, c=5):
            self.a = a
            self.b = b
            self.c = c
            super(D, self).__init__(positional='b')

    with pytest.raises(TypeError):
        E()


if __name__ == '__main__':
    pytest.main()
