# code: utf-8
from __future__ import absolute_import, print_function

import inspect
from copy import copy
from functools import partial

import six

from .compat.contextlib import suppress
from .helper import ReprHelper, PrettyReprHelper


__all__ = ['ReprHelperMixin', 'autorepr']


def autorepr(*args, **kwargs):
    """Class decorator to construct :code:`__repr__` **automatically**
    based on the arguments to ``__init__``.

    :code:`_repr_pretty_` for :py:mod:`IPython.lib.pretty` is also constructed.

    :param positional: Mark arguments as positional by number, or a list of
        argument names.

    Example:

        .. code-block:: python

            >>> @autorepr
            ... class A:
            ...     def __init__(self, a, b):
            ...         self.a = a
            ...         self.b = b

            >>> print(A(1, 2))
            A(a=1, b=2)

        .. code-block:: python

            >>> @autorepr(positional=1)
            ... class B:
            ...     def __init__(self, a, b):
            ...         self.a = a
            ...         self.b = b

            >>> print(A(1, 2))
            A(1, b=2)

    .. versionadded:: 1.5.0
    """
    cls = positional = None

    # We allow using @autorepr or @autorepr(positional=...), so check
    # how we were called.

    if args and not kwargs:
        if len(args) != 1:
            raise TypeError('Class must be only positional argument.')


        cls, = args

        if not isinstance(cls, type):
            raise TypeError(
                "The sole positional argument must be a class. To use the "
                "'positional' argument, use a keyword.")

    elif not args and kwargs:
        try:
            positional = kwargs.pop('positional')
        except KeyError:
            raise TypeError(
                "Missing required keyword-only argument: 'positional'")

    elif (args and kwargs) or (not args and not kwargs):
        raise TypeError(
            "Must pass class or keyword-only argument 'positional'")

    # Define the methods we'll add to the decorated class.

    def __repr__(self):
        return self.__class__._repr_formatstr.format(self=self)

    def _repr_pretty_(self, p, cycle):
        """Pretty printer for :class:`IPython.lib.pretty`"""
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

    if cls is not None:
        return _autorepr_decorate(
            cls, positional=positional, repr=__repr__,
            repr_pretty=_repr_pretty_)
    elif positional is not None:
        return partial(
            _autorepr_decorate, positional=positional, repr=__repr__,
            repr_pretty=_repr_pretty_)


def _autorepr_decorate(cls, positional, repr, repr_pretty):
    cls._repr_clsname = cls.__name__
    cls._repr_positional = positional

    # Support Python 3 and Python 2 argspecs,
    # including keyword only arguments
    try:
        argspec = inspect.getfullargspec(cls.__init__)
    except AttributeError:
        argspec = inspect.getargspec(cls.__init__)

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
    elif isinstance(positional, six.string_types):
        positional = [positional]

    # Ensure positional args can't follow keyword args.
    keyword_started = None

    # _repr_pretty_ uses lists for the pretty printer calls
    cls._repr_pretty_positional_args = list()
    cls._repr_pretty_keyword_args = list()

    # Construct format string for __repr__
    repr_parts = ['{self.__class__.__name__}', '(']
    for i, arg in enumerate(fun_args):
        if i:
            repr_parts.append(', ')

        if arg in positional:
            repr_parts.append('{{self.{0}!r}}'.format(arg))
            cls._repr_pretty_positional_args.append(arg)

            if arg in kwonly:
                raise ValueError("keyword only argument '{}' cannot"
                                 " be positional".format(arg))
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

    cls.__repr__ = repr
    cls._repr_pretty_ = repr_pretty

    return cls


class ReprHelperMixin(object):
    """Mixin to provide :code:`__repr__` and :code:`_repr_pretty_` for
    :py:mod:`IPython.lib.pretty` from user defined :code:`_repr_helper_`
    function.

    For full API, see :py:class:`represent.helper.BaseReprHelper`.

    .. code-block:: python

        def _repr_helper_(self, r):
            r.positional_from_attr('attrname')
            r.positional_with_value(value)
            r.keyword_from_attr('attrname')
            r.keyword_from_attr('keyword', 'attrname')
            r.keyword_with_value('keyword', value)

    .. versionadded:: 1.3
    """

    __slots__ = ()

    def __repr__(self):
        r = ReprHelper(self)
        self._repr_helper_(r)
        return str(r)

    def _repr_pretty_(self, p, cycle):
        with PrettyReprHelper(self, p, cycle) as r:
            self._repr_helper_(r)
