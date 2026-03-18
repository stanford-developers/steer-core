# steer-core

[![Tests](https://github.com/stanford-developers/steer-core/actions/workflows/tests.yml/badge.svg)](https://github.com/stanford-developers/steer-core/actions/workflows/tests.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://stanford-developers.github.io/steer-core/)

Base utilities for the OpenCell platform: constants, mixins (Serializer, Validation, Plotter), decorators, and the DataManager REST API client.

## Install

```bash
pip install -e .
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENCELL_ENV` | No | `production` | `development` = local SQLite, no auth. `production` = REST API + Cognito auth. |
| `API_URL` | In production | — | Base URL of the deployed REST API (e.g. `https://59xitvvsf2.execute-api.us-east-2.amazonaws.com/production`) |
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

### Development mode (`OPENCELL_ENV=development`)

- `SerializerMixin.from_database()` uses the local SQLite database via `steer_opencell_data.DataManager`
- No network calls, works fully offline
- Requires `steer-opencell-data` installed with `database.db`
- Use this when developing new cells locally before publishing via the CLI migration tool (`steer-opencell-data` CLI)

### Production mode (`OPENCELL_ENV=production` or unset)

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
| `get_{type}_materials(most_recent)` | 9 material-specific convenience methods |
| `insert_data(table, df)` | Upload blob to S3 via presigned URL |
| `remove_data(table, condition)` | Soft-delete via API |
| `fork_cell(table, name, new_name)` | Fork cell (auth required) |
| `publish_cell(table, name, new_name)` | Publish cell (admin only) |
| `check_name_available(name)` | Check name uniqueness across all cell tables |
| `set_token(token)` | Set JWT for authenticated requests |

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

## Quick Start

```python
from steer_core import ValidationMixin, SerializerMixin, DunderMixin

class MyComponent(ValidationMixin, SerializerMixin, DunderMixin):
    def __init__(self, name: str, mass: float):
        self._name = name
        self._mass = mass

    @property
    def name(self) -> str:
        return self._name

    @property
    def mass(self) -> float:
        return self._mass

comp = MyComponent("cathode", 0.5)
data = comp.serialize()
restored = MyComponent.deserialize(data)
assert comp == restored
```

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

See [LICENCE.txt](LICENCE.txt) for full terms.

Contributions require signing a [Contributor License Agreement](CLA.md).
