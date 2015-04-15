## Represent
[![PyPI Version][ppi]][ppl] [![Python Version][pvi]][pvl] [![MIT License][mli]][mll]

  [ppi]: http://img.shields.io/pypi/v/represent.svg?style=flat-square
  [ppl]: https://pypi.python.org/pypi/represent/
  [pvi]: https://img.shields.io/badge/python-2.7%2C%203-brightgreen.svg?style=flat-square
  [pvl]: https://www.python.org/downloads/
  [mli]: http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
  [mll]: https://raw.githubusercontent.com/RazerM/represent/master/LICENSE

### Installation

```bash
$ pip install represent
```

### Automatic Generation

```python
from represent import RepresentationMixin


class Rectangle(RepresentationMixin, object):
    def __init__(self, name, color, width, height):
        self.name = name
        self.color = color
        self.width = width
        self.height = height

        super(Rectangle, self).__init__()

rect = Rectangle('Timothy', 'red', 15, 4.5)
print(rect)
```

```
Rectangle(name='Timothy', color='red', width=15, height=4.5)
```

### Declarative Generation

```python
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
```

```
ContrivedExample('does something', 0.345, shape='square', color='red', miles=22.0)
```

For pretty printer support and more information, [visit the documentation][doc]!

  [doc]: http://pythonhosted.org/Represent/