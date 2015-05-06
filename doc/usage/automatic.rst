Automatic Generation
====================

In order to automatically generate a :code:`__repr__` for our class, we inherit from :py:class:`~represent.ReprMixin`.

.. note::

    Mixin classes should appear first in the list of superclasses, with the intended base class appearing last (in this case, :code:`object`, which isn't required on Python 3).

For automatic :code:`__repr__` creation, Represent assumes that the arguments for :code:`__init__` are available as instance variables.

Simple Example
--------------

.. code:: python

    from represent import ReprMixin


    class Rectangle(ReprMixin, object):
        def __init__(self, name, color, width, height):
            self.name = name
            self.color = color
            self.width = width
            self.height = height

            super(Rectangle, self).__init__()

    rect = Rectangle('Timothy', 'red', 15, 4.5)
    print(rect)

.. code-block:: none

    Rectangle(name='Timothy', color='red', width=15, height=4.5)

Pretty Printer
--------------

The :py:class:`~represent.ReprMixin` class also provides a :code:`_repr_pretty_` method for :py:mod:`IPython.lib.pretty`.

Therefore, with the simple example above, we can pretty print:

.. code:: python

    from IPython.lib.pretty import pprint

    rect.name = 'Something really long to force pretty printing line break'
    pprint(rect)

.. code-block:: none

    Rectangle('Something really long to force pretty printing line break',
              color='red',
              width=15,
              height=4.5)

Positional Arguments
--------------------

Using the :code:`positional` argument of :py:meth:`~represent.ReprMixin.__init__` prints some arguments without their keyword as shown here:

.. code:: python

    class Rectangle(ReprMixin, object):
        def __init__(self, name, color, width, height):
            self.name = name
            self.color = color
            self.width = width
            self.height = height

            super(Rectangle, self).__init__(positional=1)

    rect = Rectangle('Timothy', 'red', 15, 4.5)
    print(rect)

.. code-block:: none

    Rectangle('Timothy', color='red', width=15, height=4.5)

In this case, we passed the number of positional arguments. Similarly, we could have done any of the following:

.. code:: python

    super(Rectangle, self).__init__(positional='name')

.. code:: python

    super(Rectangle, self).__init__(positional=2)

.. code:: python

    super(Rectangle, self).__init__(positional=['name', 'color'])

Multiple Inheritance
--------------------

Let's create a :code:`Cuboid` class.

.. code:: python

    class Cuboid(Rectangle):
        def __init__(self, name, color, width, height, depth):
            self.depth = depth

            super(Cuboid, self).__init__(name, color, width, height)

    cuboid = Cuboid('Hector', 'purple', 7.2, 3.6, 1.8)
    print(cuboid)

.. code-block:: none

    Cuboid(name='Hector', color='purple', width=7.2, height=3.6, depth=1.8)

This works fine, but what if we want positional arguments? We need to modify :code:`Rectangle` to pass on arguments to :py:class:`~represent.ReprMixin`.

.. code:: python

    class Rectangle(ReprMixin, object):
        def __init__(self, name, color, width, height, *args, **kwargs):
            self.name = name
            self.color = color
            self.width = width
            self.width = width
            self.height = height

            super(Rectangle, self).__init__(*args, **kwargs)

    class Cuboid(Rectangle):
        def __init__(self, name, color, width, height, depth):
            self.depth = depth

            super(Cuboid, self).__init__(name, color, width, height, positional=1)

    cuboid = Cuboid('Hector', 'purple', 7.2, 3.6, 1.8)
    print(cuboid)

.. code-block:: none

    Cuboid('Hector', color='purple', width=7.2, height=3.6, depth=1.8)

Note that the combined :code:`super().__init__` call effectively does the following:

.. code:: python

    Rectangle.__init__(self, name, color, width, height)
    ReprMixin.__init__(self, positional=1)

Explicit is better than implicit, so we should use keyword arguments:

.. code:: python

    super(Cuboid, self).__init__(name=name, color=color, width=width,
                                 height=height, positional=1)

.. note::

    If :code:`Rectangle` did not inherit from :py:class:`~represent.ReprMixin`, :code:`Cuboid` could be written as follows:

    .. code:: python

        class Cuboid(ReprMixin, Rectangle):
            def __init__(self, name, color, width, height, depth):
                self.depth = depth

                super(Cuboid, self).__init__(positional=1, name=name, color=color,
                                             width=width, height=height)

    Note that the order of the arguments has changed (not that it matters when using keyword arguments).

Pickle Support
--------------

:py:class:`~represent.ReprMixin` contains ``__getstate__`` and ``__setstate__`` methods which initialise :py:class:`~represent.ReprMixin` (in addition to getting and setting ``self.__dict__``).

If you need to implement your own ``__getstate__`` and ``__setstate__`` methods, make sure to call ``ReprMixin.__init__(self)`` in your ``__setstate__``.

.. warning::

    Make sure you pass the same `positional` argument as you do in your own ``__init__`` method, or your representation will be different for a class first instantiated by unpickling.

.. note::

    If you do not want to inherit ``__getstate__`` and ``__setstate__``, you can subclass :py:class:`~represent.ReprMixinBase` instead.
