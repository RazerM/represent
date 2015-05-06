from __future__ import absolute_import, print_function

__all__ = ['ReprHelper', 'PrettyReprHelper']


class ReprHelper(object):
    """Object to help manual construction of :code:`__repr__`.

    It should be used as follows:

    .. code-block:: python

        def __repr__(self)
            r = ReprHelper(self)
            r.keyword_from_attr('name')
            return str(r)
    """
    def __init__(self, other):
        self.other = other
        self.other_cls = other.__class__
        self.repr_parts = [self.other_cls.__name__, '(']
        self.iarg = 0
        self.keyword_started = False

    def positional_from_attr(self, attr_name):
        """Add positional argument by retrieving attribute `attr_name`

        :param str attr_name: Attribute name such that
            :code:`getattr(self, attr_name)` returns the correct value.
        """
        if self.keyword_started:
            raise ValueError('positional arguments cannot '
                             'follow keyword arguments')
        self._ensure_comma()
        self.repr_parts.append(repr(getattr(self.other, attr_name)))
        self.iarg += 1

    def positional_with_value(self, value, raw=False):
        """Add positional argument with value `value`

        :param value: Value for positional argument.
        :param bool raw: If false (default), :code:`repr(value)` is used.
            Otherwise, the value is used as is.
        """
        if self.keyword_started:
            raise ValueError('positional arguments cannot '
                             'follow keyword arguments')
        self._ensure_comma()
        if raw:
            self.repr_parts.append(value)
        else:
            self.repr_parts.append(repr(value))
        self.iarg += 1

    def keyword_from_attr(self, attr_name, name=None):
        """Add keyword argument from attribute `attr_name`

        :param str attr_name: Attribute name such that
            :code:`getattr(self, attr_name)` returns the correct value.
        :param str name: Optional name for keyword, if different than
            `attr_name`.
        """
        self.keyword_started = True
        self._ensure_comma()
        if name:
            self.repr_parts.append(
                '{}={!r}'.format(attr_name, getattr(self.other, name)))
        else:
            self.repr_parts.append(
                '{}={!r}'.format(attr_name, getattr(self.other, attr_name)))
        self.iarg += 1

    def keyword_with_value(self, name, value, raw=False):
        """Add keyword argument `name` with value `value`.

        :param str name: Keyword name.
        :param value: Value for keyword argument.
        :param bool raw: If false (default), :code:`repr(value)` is used.
            Otherwise, the value is used as is.
        """
        self.keyword_started = True
        self._ensure_comma()
        if raw:
            self.repr_parts.append('{}={}'.format(name, value))
        else:
            self.repr_parts.append('{}={!r}'.format(name, value))
        self.iarg += 1

    def _ensure_comma(self):
        if self.iarg:
            self.repr_parts.append(', ')

    def __str__(self):
        return ''.join(self.repr_parts + [')'])


class PrettyReprHelper(object):
    """Object to help manual construction of :code:`_repr_pretty_` for
    :py:mod:`IPython.lib.pretty`.

    It should be used as follows:

    .. code-block:: python

        def __repr__(self, p, cycle)
            with PrettyReprHelper(self, p, cycle) as r:
                r.keyword_from_attr('name')
    """
    def __init__(self, other, p, cycle):
        self.other = other
        self.p = p
        self.cycle = cycle
        self.other_cls = other.__class__
        self.iarg = 0
        self.keyword_started = False

    def positional_from_attr(self, attr_name):
        """Add positional argument by retrieving attribute `attr_name`

        :param str attr_name: Attribute name such that
            :code:`getattr(self, attr_name)` returns the correct value.
        """
        if self.cycle:
            return

        if self.keyword_started:
            raise ValueError('positional arguments cannot '
                             'follow keyword arguments')
        self._ensure_comma()
        self.p.pretty(getattr(self.other, attr_name))
        self.iarg += 1

    def positional_with_value(self, value, raw=False):
        """Add positional argument with value `value`

        :param value: Value for positional argument.
        :param bool raw: If false (default), :code:`repr(value)` is used.
            Otherwise, the value is used as is.
        """
        if self.cycle:
            return

        if self.keyword_started:
            raise ValueError('positional arguments cannot '
                             'follow keyword arguments')
        self._ensure_comma()
        if raw:
            self.p.text(str(value))
        else:
            self.p.pretty(value)
        self.iarg += 1

    def keyword_from_attr(self, attr_name, name=None):
        """Add keyword argument from attribute `attr_name`

        :param str attr_name: Attribute name such that
            :code:`getattr(self, attr_name)` returns the correct value.
        :param str name: Optional name for keyword, if different than
            `attr_name`.
        """
        if self.cycle:
            return

        self.keyword_started = True
        self._ensure_comma()
        if name:
            with self.p.group(len(attr_name) + 1, attr_name + '='):
                self.p.pretty(getattr(self.other, name))
        else:
            with self.p.group(len(attr_name) + 1, attr_name + '='):
                self.p.pretty(getattr(self.other, attr_name))
        self.iarg += 1

    def keyword_with_value(self, name, value, raw=False):
        """Add keyword argument `name` with value `value`.

        :param str name: Keyword name.
        :param value: Value for keyword argument.
        :param bool raw: If false (default), :code:`repr(value)` is used.
            Otherwise, the value is used as is.
        """
        if self.cycle:
            return

        self.keyword_started = True
        self._ensure_comma()
        if raw:
            with self.p.group(len(name) + 1, name + '='):
                self.p.text(str(value))
        else:
            with self.p.group(len(name) + 1, name + '='):
                self.p.pretty(value)
        self.iarg += 1

    def _ensure_comma(self):
        if self.iarg:
            self.p.text(',')
            self.p.breakable()

    def __enter__(self):
        """Return self for use as context manager.

        Context manager calls self.close() on exit."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Call self.close() during exit from context manager."""
        if exc_type:
            return False

        self.close()

    def open(self):
        """Open group with class name.

        This is normally called by using as a context manager.
        """
        clsname = self.other_cls.__name__
        self.p.begin_group(len(clsname) + 1, clsname + '(')

    def close(self):
        """Close group with final bracket.

        This is normally called by using as a context manager.
        """
        suffix = [')']
        if self.cycle:
            self.p.text('...')
        clsname = self.other_cls.__name__
        self.p.end_group(len(clsname) + 1, ')')
