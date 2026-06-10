# Installation

## From PyPI

```bash
pip install steer-core
```

## From source (development)

```bash
git clone https://github.com/stanford-developers/steer-core.git
cd steer-core
pip install -e ".[dev]"
```

## Requirements

- Python >= 3.10
- See `pyproject.toml` for the full dependency list.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENCELL_ENV` | No | `development` | `development` = local SQLite, `production` = REST API |
| `API_URL` | In production | — | Base URL of the REST API |
| `API_TIMEOUT` | No | `30` | HTTP request timeout in seconds |
