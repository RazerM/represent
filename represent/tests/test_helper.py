from __future__ import absolute_import, division

import textwrap

import pytest
from IPython.lib.pretty import pprint, pretty

from represent import PrettyReprHelper, ReprHelper, ReprHelperMixin


def test_helper_methods():
    class ContrivedExample(object):
        def __init__(self, description, radians, shape, color, miles):
            self.description = description
            self.degrees = radians * 180 / 3.141592654
            self.shape = shape
            self._color = color
            self.km = 1.60934 * miles

        def _repr_helper(self, r):
            r.positional_from_attr('description')
            r.positional_with_value(self.degrees * 3.141592654 / 180)
            r.keyword_from_attr('shape')
            r.keyword_from_attr('color', '_color')
            r.keyword_with_value('miles', self.km / 1.60934)

        def __repr__(self):
            r = ReprHelper(self)
            self._repr_helper(r)
            return str(r)

        def _repr_pretty_(self, p, cycle):
            with PrettyReprHelper(self, p, cycle) as r:
                self._repr_helper(r)

    ce = ContrivedExample('does something', 0.345, 'square', 'red', 22)
    assert repr(ce) == ("ContrivedExample('does something', 0.345, "
                        "shape='square', color='red', miles=22.0)")
    prettystr = """
    ContrivedExample('does something',
                     0.345,
                     shape='square',
                     color='red',
                     miles=22.0)"""
    assert pretty(ce) == textwrap.dedent(prettystr).lstrip()

    class RecursionChecker(object):
        def __init__(self, a, b, c, d, e):
            self.a = a
            self.b = b
            self.c = c
            self._d = d
            self.e = e

        def _repr_helper(self, r):
            r.positional_from_attr('a')
            r.positional_with_value(self.b)
            r.keyword_from_attr('c')
            r.keyword_from_attr('d', '_d')
            r.keyword_with_value('e', self.e)

        def __repr__(self):
            r = ReprHelper(self)
            self._repr_helper(r)
            return str(r)

        def _repr_pretty_(self, p, cycle):
            with PrettyReprHelper(self, p, cycle) as r:
                self._repr_helper(r)

    rc = RecursionChecker(None, None, None, None, None)
    rc.a = rc
    rc.b = rc
    rc.c = rc
    rc._d = rc
    rc.e = rc
    prettystr = """
    RecursionChecker(RecursionChecker(...),
                     RecursionChecker(...),
                     c=RecursionChecker(...),
                     d=RecursionChecker(...),
                     e=RecursionChecker(...))"""
    assert pretty(rc) == textwrap.dedent(prettystr).lstrip()


def test_helper_mixin():
    """Verify that both __repr__ and _repr_pretty_ get called."""

    class ContrivedExample(ReprHelperMixin, object):
        def __init__(self, description, radians, shape, color, miles):
            self.description = description
            self.degrees = radians * 180 / 3.141592654
            self.shape = shape
            self._color = color
            self.km = 1.60934 * miles

        def _repr_helper_(self, r):
            r.positional_from_attr('description')
            r.positional_with_value(self.degrees * 3.141592654 / 180)
            r.keyword_from_attr('shape')
            r.keyword_from_attr('color', '_color')
            r.keyword_with_value('miles', self.km / 1.60934)

    ce = ContrivedExample('does something', 0.345, 'square', 'red', 22)
    assert repr(ce) == ("ContrivedExample('does something', 0.345, "
                        "shape='square', color='red', miles=22.0)")
    prettystr = """
    ContrivedExample('does something',
                     0.345,
                     shape='square',
                     color='red',
                     miles=22.0)"""
    assert pretty(ce) == textwrap.dedent(prettystr).lstrip()


    class ContrivedExampleKeywords(ContrivedExample):
        def _repr_helper_(self, r):
            r.positional_from_attr(attr_name='description')
            r.positional_with_value(value=self.degrees * 3.141592654 / 180)
            r.keyword_from_attr(name='shape')
            r.keyword_from_attr(name='color', attr_name='_color')
            r.keyword_with_value(name='miles', value=self.km / 1.60934)

    ce = ContrivedExampleKeywords('does something', 0.345, 'square', 'red', 22)
    assert repr(ce) == ("ContrivedExampleKeywords('does something', 0.345, "
                        "shape='square', color='red', miles=22.0)")
    prettystr = """
    ContrivedExampleKeywords('does something',
                             0.345,
                             shape='square',
                             color='red',
                             miles=22.0)"""
    assert pretty(ce) == textwrap.dedent(prettystr).lstrip()


def test_helper_parantheses():
    class A(object):
        def __repr__(self):
            r = ReprHelper(self)
            r.parantheses = ('<', '>')
            r.keyword_with_value('id', hex(id(self)), raw=True)
            return str(r)

        def _repr_pretty_(self, p, cycle):
            r = PrettyReprHelper(self, p, cycle)
            r.parantheses = ('<', '>')
            with r:
                r.keyword_with_value('id', hex(id(self)), raw=True)

    a = A()
    assert repr(a) == 'A<id={}>'.format(hex(id(a)))
    assert pretty(a) == 'A<id={}>'.format(hex(id(a)))

    # Test namedtuple for parantheses property
    r = ReprHelper(a)
    assert repr(r.parantheses) == "Parantheses(left='(', right=')')"
    r.parantheses = ('<', '>')
    assert repr(r.parantheses) == "Parantheses(left='<', right='>')"


if __name__ == '__main__':
    pytest.main()
