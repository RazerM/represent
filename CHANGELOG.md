# Change Log

## [Unreleased][unreleased]
N/A

## [1.1.0] - 2015-04-16
### Added
- Add pickle support by instantiating `RepresentationMixin` in `__setstate__`.

## [1.0.2] - 2015-04-06
### Fixed
- Improve control flow for class variable check, which could previously cause a bug if assertions were disabled.

## [1.0.1] - 2015-04-05
### Fixed
- Remove extra print statement (#1)

## [1.0] - 2015-03-28
### Changed
- Only create class variables during first instantiation.

[unreleased]: https://github.com/RazerM/represent/compare/1.1.0...HEAD
[1.1.0]: https://github.com/RazerM/represent/compare/1.0.2...1.1.0
[1.0.2]: https://github.com/RazerM/represent/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/RazerM/represent/compare/1.0...1.0.1
[1.0]: https://github.com/RazerM/represent/compare/1.0b1...1.0