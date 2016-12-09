# code: utf-8
from __future__ import absolute_import, print_function

import inspect
import sys
from functools import partial

import six

from .helper import ReprHelper, PrettyReprHelper
from .utilities import ReprInfo

try:
    from reprlib import recursive_repr
except ImportError:
    recursive_repr = None


__all__ = ['ReprHelperMixin', 'autorepr']


_DEFAULT_INCLUDE_PRETTY = True


def autorepr(*args, **kwargs):
    """Class decorator to construct :code:`__repr__` **automatically**
    based on the arguments to ``__init__``.

    :code:`_repr_pretty_` for :py:mod:`IPython.lib.pretty` is also constructed,
    unless `include_pretty=False`.

    :param positional: Mark arguments as positional by number, or a list of
        argument names.
    :param include_pretty: Add a ``_repr_pretty_`` to the class (defaults to
        True).

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
    include_pretty = _DEFAULT_INCLUDE_PRETTY

    # We allow using @autorepr or @autorepr(positional=..., ...), so check
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
        valid_kwargs = {'positional', 'include_pretty'}
        invalid_kwargs = set(kwargs) - valid_kwargs

        if invalid_kwargs:
            error = 'Unexpected keyword arguments: {}'.format(invalid_kwargs)
            raise TypeError(error)

        positional = kwargs.get('positional')
        include_pretty = kwargs.get('include_pretty', include_pretty)

    elif (args and kwargs) or (not args and not kwargs):
        raise TypeError(
            'Use bare @autorepr or @autorepr(...) with keyword args.')

    # Define the methods we'll add to the decorated class.

    def __repr__(self):
        return self.__class__._represent.fstr.format(self=self)

    if recursive_repr is not None:
        __repr__ = recursive_repr()(__repr__)

    _repr_pretty_ = None
    if include_pretty:
        _repr_pretty_ = _make_repr_pretty()

    if cls is not None:
        return _autorepr_decorate(cls, repr=__repr__, repr_pretty=_repr_pretty_)
    else:
        return partial(
            _autorepr_decorate, repr=__repr__, repr_pretty=_repr_pretty_,
            positional=positional, include_pretty=include_pretty)


def _make_repr_pretty():
    def _repr_pretty_(self, p, cycle):
        """Pretty printer for :class:`IPython.lib.pretty`"""
        cls = self.__class__
        clsname = cls.__name__

        if cycle:
            p.text('{}(...)'.format(clsname))
        else:
            positional_args = cls._represent.args
            keyword_args = cls._represent.kw

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

    return _repr_pretty_


def _getparams(cls):
    if sys.version_info >= (3, 3):
        signature = inspect.signature(cls)
        params = list(signature.parameters)
        kwonly = {p.name for p in signature.parameters.values()
                  if p.kind == inspect.Parameter.KEYWORD_ONLY}
    else:
        argspec = inspect.getargspec(cls.__init__)
        params = argspec.args[1:]
        kwonly = set()

    return params, kwonly


def _autorepr_decorate(cls, repr, repr_pretty, positional=None,
                       include_pretty=_DEFAULT_INCLUDE_PRETTY):
    params, kwonly = _getparams(cls)

    # Args can be opted in as positional
    if positional is None:
        positional = []
    elif isinstance(positional, int):
        positional = params[:positional]
    elif isinstance(positional, six.string_types):
        positional = [positional]

    # Ensure positional args can't follow keyword args.
    keyword_started = None

    # _repr_pretty_ uses lists for the pretty printer calls
    repr_args = []
    repr_kw = []

    # Construct format string for __repr__
    repr_fstr_parts = ['{self.__class__.__name__}', '(']
    for i, arg in enumerate(params):
        if i:
            repr_fstr_parts.append(', ')

        if arg in positional:
            repr_fstr_parts.append('{{self.{0}!r}}'.format(arg))
            repr_args.append(arg)

            if arg in kwonly:
                raise ValueError("keyword only argument '{}' cannot"
                                 " be positional".format(arg))
            if keyword_started:
                raise ValueError(
                    "positional argument '{}' cannot follow keyword"
                    " argument '{}'".format(arg, keyword_started))
        else:
            keyword_started = arg
            repr_fstr_parts.append('{0}={{self.{0}!r}}'.format(arg))
            repr_kw.append(arg)

    repr_fstr_parts.append(')')

    # Store as class variable.
    cls._represent = ReprInfo(''.join(repr_fstr_parts), repr_args, repr_kw)

    cls.__repr__ = repr
    if include_pretty:
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

    if recursive_repr is not None:
        __repr__ = recursive_repr()(__repr__)

    def _repr_pretty_(self, p, cycle):
        with PrettyReprHelper(self, p, cycle) as r:
            self._repr_helper_(r)
