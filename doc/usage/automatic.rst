Automatic Generation
====================

In order to automatically generate a :code:`__repr__` for our class, we use
the :func:`~represent.core.autorepr` class decorator.

For automatic :code:`__repr__` creation, Represent assumes that the
arguments for :code:`__init__` are available as instance variables. If this
is not the case, you should use :ref:`declarative-generation`.

Simple Example
--------------

.. code:: python

    from represent import autorepr


    @autorepr
    class Rectangle:
        def __init__(self, name, color, width, height):
            self.name = name
            self.color = color
            self.width = width
            self.height = height

    rect = Rectangle('Timothy', 'red', 15, 4.5)
    print(rect)

.. code-block:: none

    Rectangle(name='Timothy', color='red', width=15, height=4.5)

Pretty Printer
--------------

:func:`~represent.core.autorepr` also provides a
:code:`_repr_pretty_` method for :mod:`IPython.lib.pretty`.

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

Using the :code:`positional` argument of :func:`~represent.core.autorepr`
prints some arguments without their keyword as shown here:

.. code:: python

    @autorepr(positional=1)
    class Rectangle:
        def __init__(self, name, color, width, height):
            self.name = name
            self.color = color
            self.width = width
            self.height = height

    rect = Rectangle('Timothy', 'red', 15, 4.5)
    print(rect)

.. code-block:: none

    Rectangle('Timothy', color='red', width=15, height=4.5)

In this case, we passed the number of positional arguments. Similarly, we
could have done any of the following:

.. code:: python

    @autorepr(positional='name')

.. code:: python

    @autorepr(positional=2)

.. code:: python

    @autorepr(positional=['name', 'color'])

Inheritance
-----------


Using :func:`~represent.core.autorepr` is like defining the following
method on the base class:

.. code-block:: python

    def __repr__(self):
        return '{self.__class__.__name__}({self.a}, {self.b})'.format(self=self)

Therefore, subclasses will correctly show their own class name, but showing
the same attributes as the base class's ``__init__``.

.. code-block:: python

    @autorepr
    class Rectangle:
        def __init__(self, width, height):
            self.width = width
            self.height = height

    class Cuboid(Rectangle):
        def __init__(self, width, height, depth):
            super().__init__(width, height)
            self.depth = depth

    rectangle = Rectangle(1, 2)
    print(rectangle)

    cuboid = Cuboid(1, 2, 3)
    print(cuboid)

Clearly, ``Cuboid.__repr__`` is incorrect in this case:

.. code-block:: none

    Rectangle(width=1, height=2)
    Cuboid(width=1, height=2)

This is easily fixed by using :func:`~represent.core.autorepr` on
subclasses if their arguments are different:

.. code-block:: python

    @autorepr
    class Cuboid(Rectangle):
        def __init__(self, width, height, depth):
            super().__init__(width, height)
            self.depth = depth

Pickle Support
--------------

The deprecated :class:`~represent.deprecated.ReprMixin` (the predecessor to
:func:`~represent.core.autorepr`) class required special care when using
pickle since it created ``__repr__`` during ``__init__``.

:func:`~represent.core.autorepr` has no such limitations, as it creates
``__repr__`` when the class is created.
