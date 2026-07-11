## Represent

[![PyPI Version][ppi]][ppl] [![Documentation][di]][dl] [![CI Status][gai]][gal] [![Coverage][cvi]][cvl] [![Python Version][pvi]][pvl] [![MIT License][mli]][mll]

[ppi]: https://img.shields.io/pypi/v/represent.svg
[ppl]: https://pypi.org/project/represent/
[pvi]: https://img.shields.io/pypi/pyversions/represent.svg
[pvl]: https://www.python.org/downloads/
[mli]: https://img.shields.io/badge/license-MIT-blue.svg
[mll]: https://raw.githubusercontent.com/RazerM/represent/master/LICENSE
[di]: https://img.shields.io/badge/docs-latest-brightgreen.svg
[dl]: https://represent.readthedocs.io/en/latest/
[gai]: https://github.com/RazerM/represent/actions/workflows/ci.yml/badge.svg?branch=master
[gal]: https://github.com/RazerM/represent/actions/workflows/ci.yml
[cvi]: https://codecov.io/gh/RazerM/represent/graph/badge.svg
[cvl]: https://codecov.io/gh/RazerM/represent

### Installation

```bash
$ pip install represent
```

### Automatic Generation

```python
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
```

```
Rectangle(name='Timothy', color='red', width=15, height=4.5)
```

### Declarative Generation

```python
from represent import ReprHelperMixin


class ContrivedExample(ReprHelperMixin, object):
    def __init__(self, description, radians, shape, color, miles):
        self.description = description
        self.degrees = radians * 180 / 3.141592654
        self.shape = shape
        self._color = color
        self.km = 1.60934 * miles

    def _repr_helper_(self, r):
        r.positional_from_attr('description')
        r.positional_with_value(self.degrees * 3.141592654 / 180)
        r.keyword_from_attr('shape')
        r.keyword_from_attr('color', '_color')
        r.keyword_with_value('miles', self.km / 1.60934)

ce = ContrivedExample('does something', 0.345, 'square', 'red', 22)

print(ce)
from IPython.lib.pretty import pprint
pprint(ce)
```

```
ContrivedExample('does something', 0.345, shape='square', color='red', miles=22.0)
ContrivedExample('does something',
                 0.345,
                 shape='square',
                 color='red',
                 miles=22.0)
```
