from __future__ import absolute_import, print_function

import inspect

from .compat.contextlib import suppress


__all__ = ['ReprMixin', 'ReprMixinBase', 'ReprHelper', 'PrettyReprHelper']

try:
    basestring
except NameError:  # Python 3
    basestring = str


class ReprMixinBase(object):
    """Mixin to construct :code:`__repr__` for named arguments **automatically**.

    :code:`_repr_pretty_` for :py:mod:`IPython.lib.pretty` is also constructed.

    :param positional: Mark arguments as positional by number, or a list of
        argument names.

    .. note::

        Unconsumed arguments are passed on to :code:`__init__` of the next
        superclass.
    """

    def __init__(self, positional=None, *args, **kwargs):
        cls = self.__class__
        # On first init, class variables for repr won't exist.
        #
        # Subclasses created after an initialisation of the superclass
        # will require the repr class variables to be created for the new
        # class.
        if (not hasattr(cls, '_repr_clsname')
                or cls._repr_clsname != cls.__name__):
            cls._repr_clsname = cls.__name__
            cls._repr_positional = positional

            # Support Python 3 and Python 2 argspecs,
            # including keyword only arguments
            try:
                argspec = inspect.getfullargspec(self.__init__)
            except AttributeError:
                argspec = inspect.getargspec(self.__init__)

            fun_args = argspec.args[1:]
            kwonly = set()
            with suppress(AttributeError):
                fun_args.extend(argspec.kwonlyargs)
                kwonly.update(argspec.kwonlyargs)

            # Args can be opted in as positional
            if positional is None:
                positional = []
            elif isinstance(positional, int):
                positional = fun_args[:positional]
            elif isinstance(positional, basestring):
                positional = [positional]

            # Ensure positional args can't follow keyword args.
            keyword_started = None

            # _repr_pretty_ uses lists for the pretty printer calls
            cls._repr_pretty_positional_args = list()
            cls._repr_pretty_keyword_args = list()

            # Construct format string for __repr__
            repr_parts = [cls.__name__, '(']
            for i, arg in enumerate(fun_args):
                if i:
                    repr_parts.append(', ')

                if arg in positional:
                    repr_parts.append('{{self.{0}!r}}'.format(arg))
                    cls._repr_pretty_positional_args.append(arg)

                    if arg in kwonly:
                        raise ValueError("keyword only argument '{}' cannot be"
                                         " positional".format(arg))
                    if keyword_started:
                        raise ValueError(
                            "positional argument '{}' cannot follow keyword"
                            " argument '{}'".format(arg, keyword_started))
                else:
                    keyword_started = arg
                    repr_parts.append('{0}={{self.{0}!r}}'.format(arg))
                    cls._repr_pretty_keyword_args.append(arg)

            repr_parts.append(')')

            # Store as class variable.
            cls._repr_formatstr = ''.join(repr_parts)

        # Pass on args for cooperative multiple inheritance.
        super(ReprMixinBase, self).__init__(*args, **kwargs)

    def __repr__(self):
        return self.__class__._repr_formatstr.format(self=self)

    def _repr_pretty_(self, p, cycle):
        """Pretty printer for IPython.lib.pretty"""
        cls = self.__class__
        clsname = cls.__name__

        if cycle:
            p.text('{}(...)'.format(clsname))
        else:
            positional_args = cls._repr_pretty_positional_args
            keyword_args = cls._repr_pretty_keyword_args

            with p.group(len(clsname) + 1, clsname + '(', ')'):
                for i, positional in enumerate(positional_args):
                    if i:
                        p.text(',')
                        p.breakable()
                    p.pretty(getattr(self, positional))

                for i, keyword in enumerate(keyword_args,
                                            start=len(positional_args)):
                    if i:
                        p.text(',')
                        p.breakable()
                    with p.group(len(keyword) + 1, keyword + '='):
                        p.pretty(getattr(self, keyword))


class ReprMixin(ReprMixinBase):
    __doc__ = ReprMixinBase.__doc__

    # To enable pickle support, we must ensure __init__ gets called. __new__
    # could be used instead, but we can only make pickle call __new__ when
    # using protocol 2 and above.
    #
    # Provide default __getstate__ and __setstate__ which calls __init__
    # Subclasses that implement these must call ReprMixin.__init__
    # in __setstate__.
    def __getstate__(self):
        return (self.__class__._repr_positional, self.__dict__)

    def __setstate__(self, d):
        positional, real_dict = d
        ReprMixin.__init__(self, positional)
        self.__dict__.update(real_dict)


class ReprHelper(object):
    """Object to help manual construction of :code:`__repr__`.

    It should be used as follows:

    .. code:: python

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

    .. code:: python

        def __repr__(self, p, cycle)
            with PrettyReprHelper(self, p, cycle) as r:
                r.keyword_from_attr('name')
    """
    def __init__(self, other, p, cycle):
        self.other = other
        self.p = p
        self.cycle = cycle
        self.other_cls = other.__class__
        clsname = self.other_cls.__name__
        p.begin_group(len(clsname) + 1, clsname + '(')
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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Call self.close() during exit from context manager."""
        if exc_type:
            return False

        self.close()

    def close(self):
        """Add closing bracket."""
        suffix = [')']
        if self.cycle:
            self.p.text('...')
        clsname = self.other_cls.__name__
        self.p.end_group(len(clsname) + 1, ')')
