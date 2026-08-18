# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.22] - 2026-08-18

### Fixed
- **`MMGAL_TO_GAL` / `GAL_TO_MMGAL` were swapped.** 1 MMgal = 1e6 gal, so
  `MMGAL_TO_GAL` is now `1e6` and `GAL_TO_MMGAL` is `1e-6` — each value was off
  by a factor of 1e12. Downstream `steer-ccus-tea` multiplies ethanol plant
  capacities by `Units.MMGAL_TO_GAL`, so those capacities were twelve orders of
  magnitude too small.
- `__version__` had regressed to `0.2.18` in a merge, so the 0.2.20 and 0.2.21
  bumps never reached the published metadata. This release carries the 0.2.20
  performance work and the 0.2.21 deserialization hardening below.

### Changed
- `msgpack` pin bumped from 1.1.1 to 1.2.1.

## [0.2.21] - 2026-08-17

### Security
- **`SerializerMixin.deserialize` no longer resolves arbitrary class paths.**
  Deserialization read `_class` / `__enum__.class` strings out of the payload and
  passed them to `importlib.import_module` + `getattr`; the `__enum__` branch then
  *called* the result with a payload-supplied argument, so a crafted file could
  reach any importable callable (e.g.
  `{"__enum__": true, "class": "os.system", "value": "..."}`). Class resolution is
  now gated by an allowlist of top-level packages (`steer_core`,
  `steer_materials`, `steer_opencell_design`) and the resolved object must be a
  class of the expected kind — a `SerializerMixin` subclass for objects, an `Enum`
  subclass for enums. Rejections raise the new `UnsafeClassPathError` (a
  `ValueError` subclass, so existing `except ValueError` callers are unaffected).
  Anything that loads a `.ocd` file from an untrusted source (uploads in the
  OpenCell apps) should take this release.
- Added `allow_class_roots(*roots)` for downstream packages that serialize their
  own `SerializerMixin` subclasses and need their root permitted.

## [0.2.20] - 2026-08-10

### Changed
- `CoordinateMixin.get_radius_of_points` is ~10-25x faster on dense point
  clouds: inputs above 4096 points are reduced to their outer rim (max-radius
  candidates per angular bin around the centroid) before the shapely
  minimum-bounding-circle call, and the redundant `pd.isna` scan on float
  arrays was removed. Results are identical to sub-micrometre precision for
  star-shaped clouds such as jelly-roll cross-sections.

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
