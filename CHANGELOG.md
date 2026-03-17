# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
