.. _declarative-generation:

Declarative Generation
======================

Helper Mixin
------------

If you cannot use, or prefer not to use :class:`~represent.core.ReprMixin`,
there is an alternative declarative syntax.

:class:`~represent.core.ReprHelperMixin` provides ``__repr__`` and
``_repr_pretty_`` (for :mod:`IPython.lib.pretty`), both of which look for a
user defined function called ``_repr_helper_``.

All possible method calls on the passed object `r` are shown here:

.. code:: python

    def _repr_helper_(self, r):
        r.positional_from_attr('attrname')
        r.positional_with_value(value)
        r.keyword_from_attr('attrname')
        r.keyword_from_attr('keyword', 'attrname')
        r.keyword_with_value('keyword', value)

The passed object, `r`, is a :class:`~represent.helper.ReprHelper` or
:class:`~represent.helper.PrettyReprHelper` instance, depending on whether
``__repr__`` or ``_repr_pretty_`` was called. These classes have an
identical API after instantiation (which is handled by the mixin class).

.. code-block:: python
    :linenos:
    :emphasize-lines: 22

    from datetime import datetime
    from IPython.lib.pretty import pprint
    from represent import ReprHelperMixin


    class ContrivedExample(ReprHelperMixin, object):
        def __init__(self, description, radians, shape, color, miles, cls):
            self.description = description
            self.degrees = radians * 180 / 3.141592654
            self.shape = shape
            self._color = color
            self.km = 1.60934 * miles
            self.cls = cls

        def _repr_helper_(self, r):
            r.positional_from_attr('description')
            r.positional_with_value(self.degrees * 3.141592654 / 180)
            r.keyword_from_attr('shape')
            r.keyword_from_attr('color', '_color')
            r.keyword_with_value('miles', self.km / 1.60934)
            qual_name = '{cls.__module__}.{cls.__name__}'.format(cls=self.cls)
            r.keyword_with_value('cls', qual_name, raw=True)


        ce = ContrivedExample('something', 0.345, 'square', 'red', 22, datetime)

        print(ce)
        pprint(ce)

.. code-block:: none

    ContrivedExample('does something', 0.345, shape='square', color='red', miles=22.0, cls=datetime.datetime)
    ContrivedExample('does something',
                     0.345,
                     shape='square',
                     color='red',
                     miles=22.0,
                     cls=datetime.datetime)

Note that ``raw=True`` on line 22 presents the string without quotes, because
``cls='datetime.datetime'`` would be incorrect.

Manual Helpers
--------------

To use the declarative style without using
:class:`~represent.core.ReprHelperMixin`, refer to the documentation for
:class:`~represent.helper.ReprHelper` and
:class:`~represent.helper.PrettyReprHelper`.

