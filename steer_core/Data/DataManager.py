import logging
import os
import re
import time
import urllib.parse
from pathlib import Path
from typing import Optional, Union

import pandas as pd
import requests

from steer_core.Constants.Units import *

logger = logging.getLogger("steer_core.DataManager")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(name)s] %(message)s"))
    logger.addHandler(_handler)

MATERIAL_TABLES = {
    "anode_materials",
    "cathode_materials",
    "binder_materials",
    "conductive_additive_materials",
    "current_collector_materials",
    "insulation_materials",
    "separator_materials",
    "tape_materials",
    "prismatic_container_materials",
}

CELL_TABLES = {"cell_references", "teardowns", "user_designs", "cell_submissions"}

ALL_TABLES = MATERIAL_TABLES | CELL_TABLES

_MATERIAL_META_COLS = ["name", "date", "version", "reference"]
_CELL_META_COLS = [
    "name",
    "form_factor",
    "internal_construction",
    "date_created",
    "version",
    "chemistry",
    "visibility",
    "owner_id",
]

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
    """Drop-in replacement for the SQLite-based DataManager.

    Talks to the OpenCell REST API (Lambda) instead of a local database.
    All existing ``from_database()`` call sites work without changes.
    """

    _token: Optional[str] = None  # class-level JWT token

    def __init__(self, jwt_token: Optional[str] = None):
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
    def set_token(cls, token: Optional[str]) -> None:
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

    @staticmethod
    def _classify_table(table_name: str) -> str:
        """Return ``'materials'`` or ``'cells'`` based on *table_name*."""
        if table_name in MATERIAL_TABLES:
            return "materials"
        if table_name in CELL_TABLES:
            return "cells"
        raise ValueError(f"Unknown table: {table_name}")

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
            except Exception:
                pass
            raise ForbiddenError(msg)
        if resp.status_code == 404:
            msg = "Not found"
            try:
                msg = resp.json().get("error", msg)
            except Exception:
                pass
            raise NotFoundError(msg)
        if resp.status_code == 409:
            msg = "Conflict"
            try:
                msg = resp.json().get("error", msg)
            except Exception:
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
        return urllib.parse.quote(name, safe="")

    # -- Read operations ---------------------------------------------------

    def get_data(
        self,
        table_name: str,
        columns: Optional[list[str]] = None,
        condition: Optional[Union[str, list[str]]] = None,
        latest_column: Optional[str] = None,
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
        columns: Optional[list[str]],
        condition: Union[str, list[str]],
        latest_column: Optional[str],
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
        return sorted(ALL_TABLES)

    # -- Material-specific getters -----------------------------------------

    def _get_materials(self, table_name: str, most_recent: bool = True) -> pd.DataFrame:
        params = {}
        if not most_recent:
            params["most_recent"] = "false"
        data = self._request(
            "GET", f"/materials/{table_name}", auth_required=False, params=params
        )
        items = data.get("items", [])
        if not items:
            return pd.DataFrame(columns=_MATERIAL_META_COLS)
        df = pd.DataFrame(items)
        # Keep only the standard metadata columns (in order)
        available = [c for c in _MATERIAL_META_COLS if c in df.columns]
        return df[available].reset_index(drop=True)

    def get_current_collector_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("current_collector_materials", most_recent)

    def get_insulation_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("insulation_materials", most_recent)

    def get_cathode_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("cathode_materials", most_recent)

    def get_anode_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("anode_materials", most_recent)

    def get_binder_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("binder_materials", most_recent)

    def get_conductive_additive_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("conductive_additive_materials", most_recent)

    def get_separator_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("separator_materials", most_recent)

    def get_tape_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("tape_materials", most_recent)

    def get_prismatic_container_materials(self, most_recent: bool = True) -> pd.DataFrame:
        return self._get_materials("prismatic_container_materials", most_recent)

    # -- Write operations --------------------------------------------------

    def insert_data(self, table_name: str, data: pd.DataFrame) -> None:
        """Save a cell to the API.

        Extracts ``name`` and ``object`` (serialized blob) from the DataFrame,
        then uploads via presigned URL.
        """
        if data.empty:
            return

        for _, row in data.iterrows():
            name = row["name"]
            encoded_name = self._encode(name)

            # Build metadata body
            body: dict = {"update_object": True}
            for col in ["form_factor", "internal_construction", "chemistry", "version"]:
                if col in row.index and pd.notna(row[col]):
                    body[col] = row[col]

            resp = self._request(
                "PUT",
                f"/cells/{table_name}/{encoded_name}",
                auth_required=True,
                json=body,
            )

            # Upload blob to presigned URL
            upload_url = resp.get("upload_url")
            if upload_url and "object" in row.index and row["object"] is not None:
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

    # -- New operations (fork / publish / name check) ----------------------

    def fork_cell(self, source_table: str, source_name: str, new_name: str) -> dict:
        """Fork *source_name* into ``user_designs`` with *new_name*.

        Returns the new cell metadata dict.  Raises ``ConflictError`` if
        *new_name* is already taken.
        """
        encoded = self._encode(source_name)
        return self._request(
            "POST",
            f"/cells/{source_table}/{encoded}/fork",
            auth_required=True,
            json={"name": new_name},
        )

    def publish_cell(
        self,
        source_table: str,
        source_name: str,
        new_name: str,
        target_table: str | None = None,
    ) -> dict:
        """Publish *source_name* with *new_name*.

        Admin only.  Raises ``ConflictError`` if *new_name* is taken.

        Parameters
        ----------
        target_table : str, optional
            Destination table (``"cell_references"`` or ``"teardowns"``).
            Defaults to ``"cell_references"`` on the server side.
        """
        encoded = self._encode(source_name)
        body: dict = {"name": new_name}
        if target_table:
            body["target_table"] = target_table
        return self._request(
            "POST",
            f"/cells/{source_table}/{encoded}/publish",
            auth_required=True,
            json=body,
        )

    def submit_cell(self, source_table: str, source_name: str) -> dict:
        """Submit a cell from *source_table* for admin review.

        Copies the cell to ``cell_submissions``.  Only the owner (non-admin)
        can submit.  Returns the new submission metadata.
        """
        encoded = self._encode(source_name)
        return self._request(
            "POST",
            f"/cells/{source_table}/{encoded}/submit",
            auth_required=True,
        )

    def reject_cell(self, table_name: str, name: str) -> None:
        """Reject (hard-delete) a submission from *table_name*.

        Admin only.  The DynamoDB item and S3 object are permanently removed.
        """
        encoded = self._encode(name)
        self._request(
            "POST",
            f"/cells/{table_name}/{encoded}/reject",
            auth_required=True,
        )

    def check_name_available(self, name: str) -> bool:
        """Return ``True`` if *name* is available across all cell tables."""
        encoded = self._encode(name)
        data = self._request("GET", f"/cells/check-name/{encoded}", auth_required=False)
        return data.get("available", False)

    # -- Static utility (kept from SQLite DataManager) ---------------------
    # steer-opencell-data/steer_opencell_data/DataManager.py
    @staticmethod
    def read_half_cell_curve(half_cell_path: Union[str, Path]) -> pd.DataFrame:
        """Read a half-cell voltage curve from a local CSV file.

        Parameters
        ----------
        half_cell_path : str or Path
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            Columns: specific_capacity, voltage, step_id.
        """
        try:
            data = pd.read_csv(half_cell_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find the file at {half_cell_path}")
        except Exception as e:
            raise ValueError(f"Error reading file at {half_cell_path}: {str(e)}")

        if "Specific Capacity (mAh/g)" not in data.columns:
            raise ValueError(
                "The file must have a column named 'Specific Capacity (mAh/g)'"
            )
        if "Voltage (V)" not in data.columns:
            raise ValueError("The file must have a column named 'Voltage (V)'")
        if "Step_ID" not in data.columns:
            raise ValueError("The file must have a column named 'Step_ID'")

        data = (
            data.rename(
                columns={
                    "Specific Capacity (mAh/g)": "specific_capacity",
                    "Voltage (V)": "voltage",
                    "Step_ID": "step_id",
                }
            )
            .assign(
                specific_capacity=lambda x: x["specific_capacity"]
                * (H_TO_S * mA_TO_A / G_TO_KG)
            )
            .filter(["specific_capacity", "voltage", "step_id"])
            .groupby(["specific_capacity", "step_id"], group_keys=False)["voltage"]
            .max()
            .reset_index()
            .sort_values(["step_id", "specific_capacity"])
        )

        return data
