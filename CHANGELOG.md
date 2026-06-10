# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.18] - 2026-06-10

### Changed
- **Breaking:** `OPENCELL_ENV` now defaults to `development` (local SQLite via
  `steer-opencell-data`) instead of `production`. Deployments using the REST
  API must set `OPENCELL_ENV=production` explicitly.
- `from_database()` raises a clear `ImportError` with install instructions when
  `steer-opencell-data` is not installed in development mode.
- Documentation: removed deployment-specific API URL from README; clarified
  that domain-specific DataManager methods live in `steer-opencell-design`.

## [0.2.11] - 2026-03-17

### Added
- `PropagationMixin` for hierarchical update propagation through object trees
- `propagating_setter` decorator for automatic parent-child relationship management
- `DatumMixin` providing standardized datum coordinate properties with mm/m conversion
- `DunderMixin` class-level float property discovery via MRO introspection
- `DateTimeMixin` with `shift_years()` and `shift_months()` supporting leap day handling
- `ColorMixin` with `adjust_fill_opacity()` and color format detection
- `DataManager` REST API client as drop-in replacement for SQLite-based client
- Cell workflow operations: `fork_cell()`, `publish_cell()`, `submit_cell()`, `reject_cell()`
- `batch_updates()` context manager for efficient multi-property updates
- LZ4 compression support in `SerializerMixin` (with zlib backward compatibility)
- Comprehensive `ValidationMixin` with 15+ validation methods
- `CoordinateMixin` with polygon area calculation, coordinate rotation, and circle/square array builders

### Changed
- Serializer compression switched from zlib to LZ4 for faster performance
- `from_database()` production mode now attempts direct fetch instead of list-then-fetch

## [0.1.0] - 2024-01-01

### Added
- Initial release with core mixins, constants, and decorators
