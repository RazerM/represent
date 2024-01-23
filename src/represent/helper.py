from abc import ABCMeta, abstractmethod

from .utilities import Parantheses, inherit_docstrings

__all__ = ["ReprHelper", "PrettyReprHelper", "RichReprHelper"]


class BaseReprHelper(metaclass=ABCMeta):
    def __init__(self, other):
        self.parantheses = Parantheses(left="(", right=")")
        self.other = other
        self.other_cls = other.__class__
        self.iarg = 0
        self.keyword_started = False

    @property
    def parantheses(self):
        return self._parantheses

    @parantheses.setter
    def parantheses(self, value):
        self._parantheses = Parantheses._make(value)

    @abstractmethod
    def positional_from_attr(self, attr_name):
        """Add positional argument by retrieving attribute `attr_name`

        :param str attr_name: Attribute name such that
            :code:`getattr(self, attr_name)` returns the correct value.
        """

    @abstractmethod
    def positional_with_value(self, value, raw=False):
        """Add positional argument with value `value`

        :param value: Value for positional argument.
        :param bool raw: If false (default), :code:`repr(value)` is used.
            Otherwise, the value is used as is.
        """

    @abstractmethod
    def keyword_from_attr(self, name, attr_name=None):
        """Add keyword argument from attribute `attr_name`

        :param str name: Keyword name. Also used as attribute name such that
            :code:`getattr(self, name)` returns the correct value.
        :param str attr_name: Attribute name, if different than `name`.

        .. versionchanged:: 1.4
           Method argument names swapped, didn't make sense before.
        """

    @abstractmethod
    def keyword_with_value(self, name, value, raw=False):
        """Add keyword argument `name` with value `value`.

        :param str name: Keyword name.
        :param value: Value for keyword argument.
        :param bool raw: If false (default), :code:`repr(value)` is used.
            Otherwise, the value is used as is.
        """


@inherit_docstrings
class ReprHelper(BaseReprHelper):
    """Help manual construction of :code:`__repr__`.

    It should be used as follows:

    .. code-block:: python

        def __repr__(self)
            r = ReprHelper(self)
            r.keyword_from_attr('name')
            return str(r)

    .. versionchanged:: 1.4

        `parantheses` property added. Must be set before `str(r)` is called:

        .. code-block:: python

            def __repr__(self)
                r = ReprHelper(self)
                r.parantheses = ('<', '>')
                r.keyword_from_attr('name')
                return str(r)
    """

    def __init__(self, other):
        self.repr_parts = []
        super().__init__(other)

    def positional_from_attr(self, attr_name):
        if self.keyword_started:
            raise ValueError("positional arguments cannot follow keyword arguments")
        self._ensure_comma()
        self.repr_parts.append(repr(getattr(self.other, attr_name)))
        self.iarg += 1

    def positional_with_value(self, value, raw=False):
        if self.keyword_started:
            raise ValueError("positional arguments cannot follow keyword arguments")
        self._ensure_comma()
        value = value if raw else repr(value)
        self.repr_parts.append(value)
        self.iarg += 1

    def keyword_from_attr(self, name, attr_name=None):
        self.keyword_started = True
        self._ensure_comma()
        attr_name = attr_name or name
        self.repr_parts.append(f"{name}={getattr(self.other, attr_name)!r}")
        self.iarg += 1

    def keyword_with_value(self, name, value, raw=False):
        self.keyword_started = True
        self._ensure_comma()
        value = value if raw else repr(value)
        self.repr_parts.append(f"{name}={value}")
        self.iarg += 1

    def _ensure_comma(self):
        if self.iarg:
            self.repr_parts.append(", ")

    def __str__(self):
        beginning = [self.other_cls.__name__, self.parantheses.left]
        end = [self.parantheses.right]
        all_parts = beginning + self.repr_parts + end
        return "".join(all_parts)


class PrettyReprHelper(BaseReprHelper):
    """Help manual construction of :code:`_repr_pretty_` for
    :py:mod:`IPython.lib.pretty`.

    It should be used as follows:

    .. code-block:: python

        def _repr_pretty_(self, p, cycle)
            with PrettyReprHelper(self, p, cycle) as r:
                r.keyword_from_attr('name')

    .. versionchanged:: 1.4
        `parantheses` property added. Must be set before
        :py:meth:`PrettyReprHelper.open` is called (usually by context manager).

        .. code-block:: python

            def _repr_pretty_(self, p, cycle)
                r = PrettyReprHelper(self, p, cycle)
                r.parantheses = ('<', '>')
                with r:
                    r.keyword_from_attr('name')
    """

    def __init__(self, other, p, cycle):
        self.p = p
        self.cycle = cycle
        super().__init__(other)

    def positional_from_attr(self, attr_name):
        if self.cycle:
            return

        if self.keyword_started:
            raise ValueError("positional arguments cannot follow keyword arguments")
        self._ensure_comma()
        self.p.pretty(getattr(self.other, attr_name))
        self.iarg += 1

    def positional_with_value(self, value, raw=False):
        if self.cycle:
            return

        if self.keyword_started:
            raise ValueError("positional arguments cannot follow keyword arguments")
        self._ensure_comma()
        if raw:
            self.p.text(str(value))
        else:
            self.p.pretty(value)
        self.iarg += 1

    def keyword_from_attr(self, name, attr_name=None):
        if self.cycle:
            return

        self.keyword_started = True
        self._ensure_comma()
        attr_name = attr_name or name
        with self.p.group(len(name) + 1, name + "="):
            self.p.pretty(getattr(self.other, attr_name))
        self.iarg += 1

    def keyword_with_value(self, name, value, raw=False):
        if self.cycle:
            return

        self.keyword_started = True
        self._ensure_comma()
        with self.p.group(len(name) + 1, name + "="):
            if raw:
                self.p.text(str(value))
            else:
                self.p.pretty(value)
        self.iarg += 1

    def _ensure_comma(self):
        if self.iarg:
            self.p.text(",")
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
        self.p.begin_group(len(clsname) + 1, clsname + self.parantheses.left)

    def close(self):
        """Close group with final bracket.

        This is normally called by using as a context manager.
        """
        if self.cycle:
            self.p.text("...")
        clsname = self.other_cls.__name__
        self.p.end_group(len(clsname) + 1, self.parantheses.right)


class RawReprWrapper:
    """rich.pretty calls repr for us, so to support raw=True we need a wrapper
    object which returns str() when repr() is called.
    """

    def __init__(self, o: object):
        self._object = o

    def __repr__(self):
        return str(self._object)


class RichReprHelper(BaseReprHelper):
    """Help manual construction of :code:`__rich_repr__` for
    :py:mod:`rich.pretty`.

    It should be used as follows:

    .. code-block:: python

        def __rich_repr__(self)
            r = RichReprHelper(self)
            r.keyword_from_attr('name')
            yield from r
    """

    def __init__(self, other):
        self._tuples = []
        super().__init__(other)

    def positional_from_attr(self, attr_name):
        if self.keyword_started:
            raise ValueError("positional arguments cannot follow keyword arguments")
        self._tuples.append((None, getattr(self.other, attr_name)))

    def positional_with_value(self, value, raw=False):
        if self.keyword_started:
            raise ValueError("positional arguments cannot follow keyword arguments")
        self._tuples.append((None, RawReprWrapper(value) if raw else value))

    def keyword_from_attr(self, name, attr_name=None):
        self.keyword_started = True
        attr_name = attr_name or name
        self._tuples.append((name, getattr(self.other, attr_name)))

    def keyword_with_value(self, name, value, raw=False):
        self.keyword_started = True
        return self._tuples.append((name, RawReprWrapper(value) if raw else value))

    def __iter__(self):
        return iter(self._tuples)
