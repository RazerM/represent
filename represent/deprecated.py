# coding: utf-8
from __future__ import absolute_import, division, print_function

import inspect

import six

from .compat.contextlib import suppress

__all__ = ['ReprMixinBase', 'ReprMixin']


class ReprMixinBase(object):
    """Mixin to construct :code:`__repr__` for named arguments **automatically**.

    :code:`_repr_pretty_` for :py:mod:`IPython.lib.pretty` is also constructed.

    :param positional: Mark arguments as positional by number, or a list of
        argument names.

    .. deprecated:: 1.5.0

        Use the :func:`~represent.core.autorepr` class decorator instead.
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
            elif isinstance(positional, six.string_types):
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
    """Mixin to construct :code:`__repr__` for named arguments **automatically**.

    :code:`_repr_pretty_` for :py:mod:`IPython.lib.pretty` is also constructed.

    This class differs from :py:class:`~represent.core.ReprMixinBase` in that it
    supports unpickling by providing ``__getstate__`` and ``__setstate__``,
    ensuring :py:class:`~represent.core.ReprMixinBase` is initialised.

    :param positional: Mark arguments as positional by number, or a list of
        argument names.

    .. versionchanged:: 1.2
       ``RepresentationMixin`` renamed to ``ReprMixin``

    .. deprecated:: 1.5.0

        Use the :func:`~represent.core.autorepr` class decorator instead.
    """

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
