# Change Log

## [Unreleased][unreleased]

N/A

## [2.1.0] - 2024-01-23

### Added

- Support for `rich.pretty` to `autorepr` and `ReprHelperMixin`.
- `RichReprHelper`.

## [2.0.0] - 2023-12-30

### Changed

- Dropped support for Python < 3.8

### Removed

- All previously deprecated items.
- `represent.__version__` etc. use `importlib.metadata` instead.

## [1.6.0.post0] - 2020-12-22

### Changed

- Modernised packaging and ensure Python 3.8-3.9 are tested on CI. No
  functional changes.

## [1.6.0] - 2019-01-30

### Added

- `autorepr` and `ReprHelperMixin` now use [`reprlib.recursive_repr`][rrr] if
  available. (#3)

### Changed

- `autorepr` now assigns one `namedtuple` to `cls._represent` instead of using
  three different class variables as before.

### Fixed

- Deprecation warnings were always raised instead of only when deprecated
  names were imported.

[rrr]: https://docs.python.org/3.5/library/reprlib.html#reprlib.recursive_repr

## [1.5.1] - 2016-05-29

### Added

- More tests for areas missing from code coverage.
- Links in the README to readthedocs and codecov.

### Fixed

- `autorepr` wouldn't create methods if a subclass had the same name as its
  parent. This check has been removed.

## [1.5.0] - 2016-05-25

### Added

- `autorepr` class decorator to replace `ReprMixin`. `autorepr` is a much
  cleaner solution, moving errors to class creation time instead of during
  `__init__`. There are no caveats with pickling anymore.

### Deprecated

The following names will raise deprecation warnings. They will be removed
completely in 2.0.0.

- `ReprMixin`
- `ReprMixinBase`

## [1.4.1] - 2016-03-11

### Fixed

- `__slots__` added to `ReprHelperMixin` to allow subclasses to use `__slots__`.

## [1.4.0] - 2015-09-02

### Added

- `BaseReprHelper`, base class for `ReprHelper` and `PrettyReprHelper` to handle
  common functionality and enforce same API and docstrings.
- `BaseReprHelper.parantheses` tuple can be set to something other than normal
  brackets, e.g. `('<', '>')`

### Fixed

- `BaseReprHelper.keyword_from_attr` parameter names swapped. `attr_name` used
  to refer to keyword name, which doesn't make sense.

## [1.3.0] - 2015-05-07

### Added

- `ReprHelperMixin` to simplify [manual generation][man]

[man]: http://represent.readthedocs.io/en/latest/usage/helper.html

### Fixed

- `PrettyReprHelper.positional_from_attr()` didn't check for cycle, causing
  recursion limit to be reached for self-referential objects.

## [1.2.1] - 2015-05-02

### Fixed

- `__init__.py` was missing from represent.compat, so wasn't packaged for PyPI.

## [1.2.0] - 2015-05-02

### Changed

- `RepresentationMixin` has been renamed to `ReprMixin`.
- `RepresentationHelper` has been renamed to `ReprHelper`.
- `PrettyRepresentationHelper` has been renamed to `PrettyReprHelper`.

### Added

- `ReprMixinBase` is available if user does not want to inherit `__getstate__`
  and `__setstate__` from `ReprMixin`.
- Documentation about Pickle support for ReprMixin (#2)

### Deprecated

These aliases will raise deprecation warnings:

- `RepresentationMixin`
- `RepresentationHelper`
- `PrettyRepresentationHelper`

## [1.1.0] - 2015-04-16

### Added

- Add pickle support by instantiating `RepresentationMixin` in `__setstate__`.

## [1.0.2] - 2015-04-06

### Fixed

- Improve control flow for class variable check, which could previously cause a
  bug if assertions were disabled.

## [1.0.1] - 2015-04-05

### Fixed

- Remove extra print statement (#1)

## [1.0] - 2015-03-28

### Changed

- Only create class variables during first instantiation.

[unreleased]: https://github.com/RazerM/represent/compare/2.1.0...HEAD
[2.1.0]: https://github.com/RazerM/represent/compare/2.0.0..2.1.0
[2.0.0]: https://github.com/RazerM/represent/compare/1.6.0.post0..2.0.0
[1.6.0.post0]: https://github.com/RazerM/represent/compare/1.6.0...1.6.0.post0
[1.6.0]: https://github.com/RazerM/represent/compare/1.5.1...1.6.0
[1.5.1]: https://github.com/RazerM/represent/compare/1.5.0...1.5.1
[1.5.0]: https://github.com/RazerM/represent/compare/1.4.1...1.5.0
[1.4.1]: https://github.com/RazerM/represent/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/RazerM/represent/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/RazerM/represent/compare/1.2.1...1.3.0
[1.2.1]: https://github.com/RazerM/represent/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/RazerM/represent/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/RazerM/represent/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/RazerM/represent/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/RazerM/represent/compare/1.0...1.0.1
[1.0]: https://github.com/RazerM/represent/compare/1.0b1...1.0
