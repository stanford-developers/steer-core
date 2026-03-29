# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

import logging
import os
import re
import time
import urllib.parse

import pandas as pd
import requests

logger = logging.getLogger("steer_core.DataManager")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    logger.addHandler(_handler)

class DataManagerError(Exception):
    """Base exception for DataManager errors."""

class APIError(DataManagerError):
    """Unexpected API error (5xx or unrecognised status)."""

class AuthenticationError(DataManagerError):
    """401 — token missing or invalid."""

class ForbiddenError(DataManagerError):
    """403 — insufficient permissions."""

class NotFoundError(DataManagerError):
    """404 — resource does not exist."""

class ConflictError(DataManagerError):
    """409 — name already taken."""

class DataManager:
    """Generic REST client for the OpenCell API.

    Provides low-level ``get_data``, ``insert_data``, and ``remove_data``
    operations.  Domain-specific convenience methods (material getters,
    cell fork/publish) should live in a subclass (see
    ``steer_opencell_design.Data.OpenCellDataManager``).

    Table classification (materials vs cells endpoint routing) is driven
    by :meth:`register_tables`.  Call it once at application startup to
    map table names to resource types.
    """

    _token: str | None = None
    _material_tables: set[str] = set()
    _cell_tables: set[str] = set()
    _material_meta_cols: list[str] = []
    _cell_meta_cols: list[str] = []

    @classmethod
    def register_tables(
        cls,
        material_tables: set[str],
        cell_tables: set[str],
        material_meta_cols: list[str] | None = None,
        cell_meta_cols: list[str] | None = None,
    ) -> None:
        """Register domain-specific table names and metadata columns.

        Must be called before any ``get_data`` / ``insert_data`` calls
        so that url routing (``/materials/…`` vs ``/cells/…``) works.

        Parameters
        ----------
        material_tables : set[str]
            Table names whose API path is ``/materials/{table}``.
        cell_tables : set[str]
            Table names whose API path is ``/cells/{table}``.
        material_meta_cols : list[str], optional
            Columns returned for material listings.
        cell_meta_cols : list[str], optional
            Columns returned for cell listings.
        """
        cls._material_tables = material_tables
        cls._cell_tables = cell_tables
        if material_meta_cols is not None:
            cls._material_meta_cols = material_meta_cols
        if cell_meta_cols is not None:
            cls._cell_meta_cols = cell_meta_cols

    def __init__(self, jwt_token: str | None = None):
        self._api_url = os.environ.get("API_URL")
        if not self._api_url:
            raise DataManagerError(
                "API_URL environment variable is required. "
                "Set it to the base URL of the OpenCell REST API "
                "(e.g. https://api.opencell.example.com/production)."
            )
        self._api_url = self._api_url.rstrip("/")
        self._timeout = int(os.environ.get("API_TIMEOUT", "30"))
        self._session = requests.Session()
        if jwt_token:
            DataManager._token = jwt_token

    # -- Context manager (no-op) -------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def close(self) -> None:
        pass

    # -- Token management --------------------------------------------------

    @classmethod
    def set_token(cls, token: str | None) -> None:
        """Set the JWT token used for authenticated API requests."""
        cls._token = token

    # -- Internal helpers --------------------------------------------------

    def _headers(self, auth_required: bool = False) -> dict:
        headers: dict[str, str] = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        elif auth_required:
            raise AuthenticationError(
                "JWT token required for this operation. "
                "Call DataManager.set_token(token) first."
            )
        return headers

    @classmethod
    def _classify_table(cls, table_name: str) -> str:
        """Return ``'materials'`` or ``'cells'`` based on *table_name*."""
        if table_name in cls._material_tables:
            return "materials"
        if table_name in cls._cell_tables:
            return "cells"
        raise ValueError(
            f"Unknown table: {table_name!r}. "
            "Call DataManager.register_tables() first to register domain tables."
        )

    @staticmethod
    def _parse_condition(condition: str) -> tuple[str, str]:
        """Parse ``"name = 'LFP'"`` → ``('name', 'LFP')``.

        This is the only condition format used by ``from_database()``.
        """
        match = re.match(r"(\w+)\s*=\s*'([^']*)'", condition.strip())
        if not match:
            raise ValueError(f"Cannot parse condition: {condition}")
        return match.group(1), match.group(2)

    def _request(self, method: str, path: str, auth_required: bool = False, **kwargs):
        """Make an HTTP request and return parsed JSON (or *None* for 204)."""
        url = f"{self._api_url}{path}"
        t0 = time.perf_counter()
        resp = self._session.request(
            method,
            url,
            headers=self._headers(auth_required),
            timeout=self._timeout,
            **kwargs,
        )
        elapsed = (time.perf_counter() - t0) * 1000
        logger.info("[API] %s %s -> %d (%d ms)", method, path, resp.status_code, elapsed)
        if resp.status_code == 204:
            return None
        if resp.status_code == 401:
            raise AuthenticationError("Authentication required")
        if resp.status_code == 403:
            msg = "Forbidden"
            try:
                msg = resp.json().get("error", msg)
            except (ValueError, KeyError):
                pass
            raise ForbiddenError(msg)
        if resp.status_code == 404:
            msg = "Not found"
            try:
                msg = resp.json().get("error", msg)
            except (ValueError, KeyError):
                pass
            raise NotFoundError(msg)
        if resp.status_code == 409:
            msg = "Conflict"
            try:
                msg = resp.json().get("error", msg)
            except (ValueError, KeyError):
                pass
            raise ConflictError(msg)
        if resp.status_code >= 400:
            raise APIError(f"HTTP {resp.status_code}: {resp.text}")
        return resp.json()

    def _download_blob(self, download_url: str) -> bytes:
        """Download serialized object bytes from a presigned S3 URL."""
        t0 = time.perf_counter()
        resp = self._session.get(download_url, timeout=self._timeout)
        resp.raise_for_status()
        elapsed = (time.perf_counter() - t0) * 1000
        logger.info("[S3] Downloaded %.1f KB in %d ms", len(resp.content) / 1024, elapsed)
        return resp.content

    @staticmethod
    def _encode(name: str) -> str:
        # Double-encode: API Gateway decodes path parameters once automatically
        single = urllib.parse.quote(name, safe="")
        return urllib.parse.quote(single, safe="")

    # -- Read operations ---------------------------------------------------

    def get_data(
        self,
        table_name: str,
        columns: list[str] | None = None,
        condition: str | list[str] | None = None,
        latest_column: str | None = None,
    ) -> pd.DataFrame:
        """Retrieve data from the API.

        When *condition* is provided (the ``from_database()`` path), fetches a
        single item **including** the serialized object blob.  The ``object``
        column contains raw ``bytes`` — identical to what SQLite returned.

        When called **without** a condition, returns metadata-only rows (no
        ``object`` column).
        """
        resource_type = self._classify_table(table_name)
        auth = resource_type == "cells"

        if condition is not None:
            return self._get_data_with_condition(
                table_name, resource_type, columns, condition, latest_column, auth
            )

        # -- Listing (no condition) ----------------------------------------
        data = self._request("GET", f"/{resource_type}/{table_name}", auth_required=False)
        items = data.get("items", [])
        if not items:
            return pd.DataFrame()

        df = pd.DataFrame(items)

        if latest_column and latest_column in df.columns:
            df = df.sort_values(latest_column, ascending=False).head(1).reset_index(drop=True)

        if columns:
            available = [c for c in columns if c in df.columns]
            df = df[available]

        return df

    def _get_data_with_condition(
        self,
        table_name: str,
        resource_type: str,
        columns: list[str] | None,
        condition: str | list[str],
        latest_column: str | None,
        auth: bool,
    ) -> pd.DataFrame:
        """Handle ``get_data()`` when a condition is supplied."""
        # Normalise condition list to a single dict of field→value
        if isinstance(condition, list):
            parsed = dict(self._parse_condition(c) for c in condition)
        else:
            field, value = self._parse_condition(condition)
            parsed = {field: value}

        name = parsed.get("name")
        if name is None:
            raise ValueError(
                f"Condition must include 'name': {condition}"
            )

        encoded_name = self._encode(name)
        data = self._request(
            "GET",
            f"/{resource_type}/{table_name}/{encoded_name}",
            auth_required=False,
        )

        # Download the object blob via presigned URL
        download_url = data.get("download_url")
        if not download_url:
            raise APIError(
                f"No download_url in response for {table_name}/{name}"
            )
        blob = self._download_blob(download_url)

        # Build a single-row DataFrame matching the SQLite schema
        row: dict = {"name": data["name"], "object": blob}

        if resource_type == "materials":
            row["date"] = data.get("date")
            row["version"] = data.get("version")
            row["reference"] = data.get("reference")
        else:
            row["form_factor"] = data.get("form_factor")
            row["internal_construction"] = data.get("internal_construction")
            row["date_created"] = data.get("date_created")
            row["version"] = data.get("version")
            row["chemistry"] = data.get("chemistry")

        df = pd.DataFrame([row])

        if latest_column and latest_column in df.columns:
            df = df.sort_values(latest_column, ascending=False).head(1).reset_index(drop=True)

        if columns:
            available = [c for c in columns if c in df.columns]
            df = df[available]

        return df

    def get_unique_values(self, table_name: str, column_name: str) -> list:
        """Return unique values for *column_name* from the listing endpoint."""
        resource_type = self._classify_table(table_name)
        data = self._request("GET", f"/{resource_type}/{table_name}", auth_required=False)
        items = data.get("items", [])
        seen: set = set()
        result: list = []
        for item in items:
            val = item.get(column_name)
            if val is not None and val not in seen:
                seen.add(val)
                result.append(val)
        return result

    def get_table_names(self) -> list[str]:
        return sorted(self._material_tables | self._cell_tables)

    # -- Write operations --------------------------------------------------

    def insert_data(self, table_name: str, data: pd.DataFrame) -> None:
        """Save a cell to the API.

        Extracts ``name`` and ``object`` (serialized blob) from the DataFrame,
        then uploads via presigned URL.
        """
        if data.empty:
            return

        columns = set(data.columns)
        meta_cols = {"form_factor", "internal_construction", "chemistry", "version"}

        for row in data.to_dict("records"):
            name = row["name"]
            encoded_name = self._encode(name)

            body: dict = {"update_object": True}
            for col in meta_cols & columns:
                if pd.notna(row[col]):
                    body[col] = row[col]

            resp = self._request(
                "PUT",
                f"/cells/{table_name}/{encoded_name}",
                auth_required=True,
                json=body,
            )

            upload_url = resp.get("upload_url")
            if upload_url and "object" in columns and row.get("object") is not None:
                blob = row["object"]
                if isinstance(blob, str):
                    blob = blob.encode("latin-1")
                upload_resp = self._session.put(
                    upload_url,
                    data=blob,
                    headers={"Content-Type": "application/octet-stream"},
                    timeout=self._timeout,
                )
                upload_resp.raise_for_status()

    def remove_data(self, table_name: str, condition: str) -> None:
        """Delete a cell via the API."""
        _, name = self._parse_condition(condition)
        encoded_name = self._encode(name)
        self._request(
            "DELETE",
            f"/cells/{table_name}/{encoded_name}",
            auth_required=True,
        )

    def create_table(self, table_name: str, columns: dict):
        raise NotImplementedError("create_table() is not supported by the REST API")

    def drop_table(self, table_name: str):
        raise NotImplementedError("drop_table() is not supported by the REST API")
