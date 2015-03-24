Manual Generation
=================

Representation Helper
---------------------

:py:class:`~represent.RepresentationHelper` provides a simple declarative syntax to produce a :code:`__repr__` for your class.

.. code:: python

    from represent import RepresentationHelper


    class ContrivedExample(object):
        def __init__(self, description, radians, shape, color, miles):
            self.description = description
            self.degrees = radians * 180 / 3.141592654
            self.shape = shape
            self._color = color
            self.km = 1.60934 * miles

        def __repr__(self):
            r = RepresentationHelper(self)
            r.positional_from_attr('description')
            r.positional_with_value(self.degrees * 3.141592654 / 180)
            r.keyword_from_attr('shape')
            r.keyword_from_attr('color', '_color')
            r.keyword_with_value('miles', self.km / 1.60934)
            return str(r)

    ce = ContrivedExample('does something', 0.345, 'square', 'red', 22)
    print(ce)

.. code-block:: none

    ContrivedExample('does something', 0.345, shape='square', color='red', miles=22.0)

Pretty Representation Helper
----------------------------

In addition to the :py:class:`~represent.RepresentationHelper` class, there is also a :py:class:`~represent.PrettyRepresentationHelper` class which helps provide a :code:`_repr_pretty_` method for :py:mod:`IPython.lib.pretty`

The only difference is the additional initialisation variables required by :code:`_repr_pretty_`:

.. code:: python

    from represent import PrettyRepresentationHelper, RepresentationHelper

    class ContrivedExample(object):
        def __init__(self, description, radians, shape, color, miles):
            self.description = description
            self.degrees = radians * 180 / 3.141592654
            self.shape = shape
            self._color = color
            self.km = 1.60934 * miles

        def __repr__(self):
            r = RepresentationHelper(self)
            r.positional_from_attr('description')
            r.positional_with_value(self.degrees * 3.141592654 / 180)
            r.keyword_from_attr('shape')
            r.keyword_from_attr('color', '_color')
            r.keyword_with_value('miles', self.km / 1.60934)
            return str(r)

        def _repr_pretty(self, p, cycle):
            with PrettyRepresentationHelper(self, p, cycle) as r:
                r.positional_from_attr('description')
                r.positional_with_value(self.degrees * 3.141592654 / 180)
                r.keyword_from_attr('shape')
                r.keyword_from_attr('color', '_color')
                r.keyword_with_value('miles', self.km / 1.60934)

Note that we use a context manager here, which ensures the closing bracket is added to the end. By design, the API after initialisation is identical. As such, let's invoke the `DRY principle`_:

.. _`DRY principle`: http://en.wikipedia.org/wiki/Don%27t_repeat_yourself

.. code:: python

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
            r = RepresentationHelper(self)
            self._repr_helper(r)
            return str(r)

        def _repr_pretty(self, p, cycle):
            with PrettyRepresentationHelper(self, p, cycle) as r:
                self._repr_helper(r)

.. code:: python

    from IPython.lib.pretty import pprint

    ce = ContrivedExample('does something', 0.345, 'square', 'red', 22)
    ce.description = 'Something really long to force pretty printer line break'
    pprint(ce)

.. code-block:: none

    ContrivedExample('Something really long to force pretty printer line break',
                     0.345,
                     shape='square',
                     color='red',
                     miles=22.0)