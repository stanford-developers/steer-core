# steer-core

[![Tests](https://github.com/stanford-developers/steer-core/actions/workflows/tests.yml/badge.svg)](https://github.com/stanford-developers/steer-core/actions/workflows/tests.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://stanford-developers.github.io/steer-core/)

Base utilities for the STEER / OpenCell platform: the mixin framework (validation, serialization, plotting, geometry, change propagation), shared constants, recalculation decorators, and the DataManager REST API client. Every domain class in the STEER ecosystem — materials, electrodes, cells — is built by composing the mixins in this package.

---

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [Mixins](#mixins)
  - [ValidationMixin](#validationmixin)
  - [SerializerMixin](#serializermixin)
  - [DunderMixin](#dundermixin)
  - [PropagationMixin](#propagationmixin)
  - [PlotterMixin](#plottermixin)
  - [CoordinateMixin](#coordinatemixin)
  - [ColorMixin](#colormixin)
  - [DataMixin](#datamixin)
  - [DatumMixin](#datummixin)
  - [DateTimeMixin](#datetimemixin)
  - [ThermodynamicsMixin](#thermodynamicsmixin)
- [Constants](#constants)
- [Decorators](#decorators)
- [Environment Variables](#environment-variables)
- [Development vs Production Mode](#development-vs-production-mode)
- [DataManager REST Client](#datamanager-rest-client)
- [STEER Ecosystem](#steer-ecosystem)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

---

## Install

```bash
pip install steer-core
```

Or from source:

```bash
git clone https://github.com/stanford-developers/steer-core.git
cd steer-core
pip install -e .
```

Requires **Python >= 3.10**.

---

## Quick Start

Domain classes are built by composing mixins:

```python
from steer_core import ValidationMixin, SerializerMixin, DunderMixin

class MyComponent(ValidationMixin, SerializerMixin, DunderMixin):
    def __init__(self, name: str, mass: float):
        self.validate_string(name, "name")
        self.validate_positive_float(mass, "mass")
        self._name = name
        self._mass = mass

    @property
    def name(self) -> str:
        return self._name

    @property
    def mass(self) -> float:
        return self._mass

comp = MyComponent("cathode", 0.5)
data = comp.serialize()                      # bytes (MessagePack + LZ4)
restored = MyComponent.deserialize(data)
assert comp == restored                      # property-aware equality from DunderMixin
```

---

## Mixins

Seven mixins are exported at the top level:

```python
from steer_core import (
    ColorMixin,
    CoordinateMixin,
    DataMixin,
    DunderMixin,
    PlotterMixin,
    SerializerMixin,
    ValidationMixin,
)
```

The rest are imported from their submodules (e.g. `from steer_core.Mixins.Propagation import PropagationMixin`).

### ValidationMixin

Static type and value validators that raise `TypeError`/`ValueError` with consistent messages. Used in every setter across the ecosystem.

```python
from steer_core import ValidationMixin

ValidationMixin.validate_type(value, (int, float), "thickness")
ValidationMixin.validate_positive_float(thickness, "thickness")
ValidationMixin.validate_fraction(porosity, "porosity")          # [0, 1]
ValidationMixin.validate_percentage(efficiency, "efficiency")    # [0, 100]
ValidationMixin.validate_string(name, "name")
ValidationMixin.validate_datum(datum)                            # 3-element numeric tuple
ValidationMixin.validate_pandas_dataframe(df, "data", column_names=["x", "y"])
ValidationMixin.validate_enum_string(mode, ControlMode, "mode")
```

### SerializerMixin

Binary serialization with MessagePack + LZ4 compression, and database loading. Handles nested objects, numpy arrays, pandas DataFrames, `datetime`, `Enum`, and object-keyed dicts.

| Method | What it does |
|--------|-------------|
| `serialize(compress=True)` | Instance → `bytes` |
| `deserialize(data)` (classmethod) | `bytes` → instance (class path stored in payload) |
| `from_database(name, table_name=None)` (classmethod) | Load a named object from the database backend (see [Development vs Production Mode](#development-vs-production-mode)) |
| `_to_dict()` / `_from_dict(data)` | Override hooks for custom serialization |

```python
blob = cell.serialize()
restored = Cell.deserialize(blob)

# Requires a _table_name on the subclass:
material = CathodeMaterial.from_database("LFP")
```

### DunderMixin

Property-aware comparison and string representation.

- `__eq__` — deep equality over all public `@property` values (numpy arrays, DataFrames, and nested objects compared correctly; Plotly traces skipped)
- `__str__` / `__repr__` — `ClassName (name)` when the object has a `.name`
- `__hash__` — identity-based, safe for mutable objects

### PropagationMixin

Parent-child change propagation for hierarchical models (cell → assembly → electrode → formulation → material). Lives in `steer_core.Mixins.Propagation`.

| Member | What it does |
|--------|-------------|
| `propagating_setter(attr_name=None, deepcopy=False)` | Setter decorator: manages parent links when a child is assigned |
| `update()` | Re-run the parent's setter for this object (triggers recalculation) |
| `propagate_changes()` | Bubble updates all the way to the root object |
| `batch_updates()` | Context manager: defer recalculation until exit |

```python
from steer_core.Mixins.Propagation import PropagationMixin, propagating_setter

class Electrode(PropagationMixin, ...):
    @property
    def formulation(self):
        return self._formulation

    @formulation.setter
    @propagating_setter()
    def formulation(self, value):
        self._formulation = value

# Change a leaf, recompute the whole tree:
formulation.active_material_fraction = 0.97
formulation.propagate_changes()

# Batch multiple changes with a single recalculation:
with cell.batch_updates():
    cell.diameter = 21
    cell.height = 70
```

### PlotterMixin

Plotly figure builders and shared layout presets used by all STEER visualizations.

- **Layout presets** — `DEFAULT_PALETTE`, `SCATTER_X_AXIS` / `SCATTER_Y_AXIS`, `SCHEMATIC_X/Y/Z_AXIS`, `BOTTOM_LEGEND`
- **Domain helpers** — `create_component_trace()` (filled cross-section traces), `plot_breakdown_sunburst()` (mass/cost roll-ups)
- **Generic plots** — `plot_scatter`, `plot_bar`, `plot_histogram`, `plot_pdf`, `plot_box`, `plot_violin`, `plot_radar`, `plot_correlation_heatmap`, and grouped variants — all return `plotly.graph_objects.Figure`

```python
fig = PlotterMixin.plot_breakdown_sunburst(cell.mass_breakdown, title="Mass", unit="g")
fig.show()
```

### CoordinateMixin

Static 2D/3D geometry utilities built on numpy and shapely.

| Method | What it does |
|--------|-------------|
| `rotate_coordinates(coords, axis, angle, center=None)` | Rotate `(N,2)` or `(N,3)` points about `x`/`y`/`z` |
| `get_area_from_points(x, y)` | Shoelace area (handles NaN-separated segments) |
| `get_radius_of_points(coords)` | Minimum bounding circle |
| `build_square_array` / `build_circle_array` | Boundary point generators |
| `extrude_footprint(x, y, datum, thickness)` | 2D footprint → 3D solid coordinates |
| `get_coordinate_intersection(coords1, coords2)` | Polygon intersection area |
| `order_coordinates_clockwise(df, plane="xy")` | Sort boundary points clockwise |

### ColorMixin

Color conversion and manipulation for Plotly figures: `rgb_tuple_to_hex()`, `get_colorway(color1, color2, n)` (n-step gradients), `adjust_fill_opacity()`, `adjust_trace_opacity()`, `get_color_format()`.

### DataMixin

Numeric data helpers: `enforce_monotonicity(array)` (PCHIP-smoothed monotonic curves, used for voltage-capacity data) and `sum_breakdowns(components, breakdown_type)` (recursive roll-up of `mass` / `cost` breakdown dicts across component trees).

### DatumMixin

Positional datum handling for components placed in 3D space. Stores the datum in meters internally, exposes millimeters through `datum`, `datum_x`, `datum_y`, `datum_z` properties. Lives in `steer_core.Mixins.Datum`.

### DateTimeMixin

Datetime parsing and arithmetic with the STEER standard formats (`YYYY-MM-DD-HH` / `YYYY-MM-DD`): `str_to_datetime()`, `datetime_to_str()`, `shift_years()`, `shift_months()` (calendar-aware), `validate_end_after_start()`. Lives in `steer_core.Mixins.DateTime`.

### ThermodynamicsMixin

Basic thermodynamic relations: `calculate_antoine_pressure(T, A, B, C)`, `calculate_antoine_temperature(P, A, B, C)`, and `calculate_ideal_gas_density(P, T, MW)`. Lives in `steer_core.Mixins.Thermodynamics`.

---

## Constants

Module-level constants shared across the ecosystem:

```python
from steer_core.Constants.Units import MM_TO_M, M_TO_MM, KG_TO_G, J_TO_WH
from steer_core.Constants.Universal import PI, R_GAS, GRAVITY, STANDARD_PRESSURE
from steer_core.Constants.Format import DEFAULT_HOUR_FMT, DEFAULT_DAY_FMT

thickness_m = thickness_mm * MM_TO_M
```

| Module | Contents |
|--------|----------|
| `Constants.Units` | Unit conversion factors — mass (`KG_TO_G`), length (`M_TO_MM`, `UM_TO_M`), time (`H_TO_S`), energy (`J_TO_WH`, `KW_TO_W`), pressure (`BAR_TO_PA`), temperature (`C_TO_K`), currency, and angles. Multiply a source-unit value by the factor to get the target unit. |
| `Constants.Universal` | Physical constants: `PI`, `TWO_PI`, `R_GAS` (8.3145 J/mol/K), `GRAVITY`, `STANDARD_PRESSURE`, `STANDARD_TEMPERATURE` |
| `Constants.Format` | Standard datetime format strings: `DEFAULT_HOUR_FMT` (`%Y-%m-%d-%H`), `DEFAULT_DAY_FMT` (`%Y-%m-%d`) |

---

## Decorators

Setter decorators that trigger recalculation of derived properties after an attribute changes.

```python
from steer_core.Decorators.General import recalculate, calculate_all_properties
from steer_core.Decorators.Coordinates import calculate_coordinates

class Electrode(...):
    @thickness.setter
    @calculate_all_properties        # calls self._calculate_all_properties() after the set
    def thickness(self, value):
        self._thickness = value

    @datum.setter
    @calculate_coordinates           # calls self._calculate_coordinates() after the set
    def datum(self, value):
        self._datum = value
```

| Decorator | Module | Triggers |
|-----------|--------|----------|
| `recalculate(*names, requires=None)` | `Decorators.General` | Factory — calls `self._calculate_<name>()` for each name, optionally gated on attribute predicates |
| `calculate_all_properties` | `Decorators.General` | `_calculate_all_properties()` |
| `calculate_bulk_properties` | `Decorators.General` | `_calculate_bulk_properties()` |
| `calculate_coordinates` | `Decorators.Coordinates` | `_calculate_coordinates()` |
| `calculate_areas` | `Decorators.Coordinates` | `_calculate_coordinates()` + `_calculate_areas()` |
| `calculate_volumes` | `Decorators.Coordinates` | `_calculate_bulk_properties()` + `_calculate_coordinates()` |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENCELL_ENV` | No | `development` | `development` = local SQLite, no auth. `production` = REST API + Cognito auth. |
| `API_URL` | In production | — | Base URL of the deployed REST API (e.g. `https://api.opencell.example.com/production`) |
| `API_TIMEOUT` | No | `30` | HTTP request timeout in seconds |

## Development vs Production Mode

Controlled by the `OPENCELL_ENV` environment variable. The helper `is_development()` from `steer_core.Data` is the single source of truth — use it anywhere you need to branch on mode.

```python
from steer_core.Data import is_development

if is_development():
    # local SQLite path
else:
    # REST API path
```

### Development mode (`OPENCELL_ENV=development` or unset)

- `SerializerMixin.from_database()` uses the local SQLite database via `steer_opencell_data.DataManager`
- No network calls, works fully offline
- Requires [steer-opencell-data](https://github.com/stanford-developers/steer-opencell-data) installed with `database.db`
- Use this when developing new cells locally before publishing via the CLI migration tool (`steer-opencell-data` CLI)

### Production mode (`OPENCELL_ENV=production`)

- `SerializerMixin.from_database()` uses the REST API via `steer_core.Data.DataManager`
- Requires `API_URL` pointing to the deployed Lambda endpoint
- JWT token passed automatically for authenticated operations (`DataManager.set_token()`)
- Logs API calls and S3 downloads to the `steer_core.DataManager` logger

## DataManager REST Client

`steer_core.Data.DataManager` — drop-in replacement for the SQLite-based DataManager. Same interface, talks to the REST API + S3 instead.

### Key methods

| Method | What it does |
|--------|-------------|
| `get_data(table, condition="name='X'")` | Fetch item + download blob from S3 presigned URL |
| `get_data(table)` (no condition) | List items — metadata only, no blob |
| `get_unique_values(table, column)` | List unique values from API |
| `get_table_names()` | List available tables |
| `insert_data(table, df)` | Upload blob to S3 via presigned URL |
| `remove_data(table, condition)` | Soft-delete via API |
| `set_token(token)` | Set JWT for authenticated requests |

Domain-specific convenience methods (e.g. `get_cathode_materials()`, `fork_cell()`, `publish_cell()`, `check_name_available()`) live in `OpenCellDataManager` in the [steer-opencell-design](https://github.com/stanford-developers/steer-opencell-design) package, which subclasses this client.

### Exceptions

| Exception | HTTP Status | When |
|-----------|-------------|------|
| `DataManagerError` | — | Base class / missing `API_URL` |
| `APIError` | 5xx | Server error |
| `AuthenticationError` | 401 | Missing or invalid token |
| `ForbiddenError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ConflictError` | 409 | Name already taken (fork/publish) |

### Logging

API calls and S3 downloads are logged to the `steer_core.DataManager` logger:

```
[steer_core.DataManager] [API] GET /materials/tape_materials/Kapton -> 200 (164 ms)
[steer_core.DataManager] [S3] Downloaded 0.2 KB in 499 ms
```

---

## STEER Ecosystem

`steer-core` is the foundation of the STEER platform:

| Package | Role |
|---|---|
| **`steer-core`** | **This package.** The mixin framework shared by all STEER packages — validation, serialization, coordinate systems, change propagation, Plotly-based plotting, and database access. |
| [`steer-materials`](https://github.com/stanford-developers/steer-materials) | Base material classes with `from_database()` support, volumetric tracking, and metal subclasses. |
| [`steer-opencell-design`](https://github.com/stanford-developers/steer-opencell-design) | The cell design API that composes materials and components into complete virtual battery cells with cost, mass, and electrochemical calculations. |
| [`steer-opencell-data`](https://github.com/stanford-developers/steer-opencell-data) | The open dataset: local SQLite database of materials, reference cell designs, and commercial cell teardowns, plus the scripts that build it. |

---

## Documentation

Full documentation is available at [stanford-developers.github.io/steer-core](https://stanford-developers.github.io/steer-core/).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Citation

If you use this software, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

steer-core is dual-licensed:

- **Open source** — [GNU Affero General Public License v3.0 or later](https://www.gnu.org/licenses/agpl-3.0) (AGPL-3.0-or-later)
- **Commercial** — A separate commercial license is available for use without AGPL-3.0 copyleft requirements. Contact [nsiemons@stanford.edu](mailto:nsiemons@stanford.edu) for details.

See [LICENSE](LICENSE) for full terms.

Contributions require signing a [Contributor License Agreement](CLA.md).
