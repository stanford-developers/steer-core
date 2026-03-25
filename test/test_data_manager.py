# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Data.DataManager (mocked HTTP)."""

import os
from unittest.mock import MagicMock

import pandas as pd
import pytest

from steer_core.Data.DataManager import (
    APIError,
    AuthenticationError,
    ConflictError,
    DataManager,
    DataManagerError,
    ForbiddenError,
    NotFoundError,
)

# Register domain tables for tests (normally done by steer_opencell_design)
_TEST_MATERIAL_TABLES = {
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
_TEST_CELL_TABLES = {"cell_references", "teardowns", "user_designs", "cell_submissions"}
DataManager.register_tables(
    material_tables=_TEST_MATERIAL_TABLES,
    cell_tables=_TEST_CELL_TABLES,
    material_meta_cols=["name", "date", "version", "reference"],
    cell_meta_cols=[
        "name", "form_factor", "internal_construction",
        "date_created", "version", "chemistry", "visibility", "owner_id",
    ],
)


@pytest.fixture(autouse=True)
def set_api_url(monkeypatch):
    """Ensure API_URL is set for all tests."""
    monkeypatch.setenv("API_URL", "https://api.example.com/production")
    DataManager._token = None


@pytest.fixture
def dm():
    d = DataManager()
    d._session = MagicMock()
    return d


class TestDataManagerInit:

    def test_missing_api_url_raises(self, monkeypatch):
        monkeypatch.delenv("API_URL", raising=False)
        with pytest.raises(DataManagerError, match="API_URL"):
            DataManager()

    def test_default_timeout(self, dm):
        assert dm._timeout == 30

    def test_custom_timeout(self, monkeypatch):
        monkeypatch.setenv("API_TIMEOUT", "60")
        dm = DataManager()
        assert dm._timeout == 60

    def test_jwt_token_set(self, monkeypatch):
        dm = DataManager(jwt_token="test-token")
        assert DataManager._token == "test-token"

    def test_context_manager(self, dm):
        with dm as d:
            assert d is dm


class TestTokenManagement:

    def test_set_token(self):
        DataManager.set_token("my-token")
        assert DataManager._token == "my-token"
        DataManager.set_token(None)
        assert DataManager._token is None

    def test_headers_with_token(self, dm):
        DataManager.set_token("bearer-token")
        headers = dm._headers()
        assert headers["Authorization"] == "Bearer bearer-token"

    def test_headers_no_token(self, dm):
        headers = dm._headers()
        assert "Authorization" not in headers

    def test_headers_auth_required_no_token_raises(self, dm):
        with pytest.raises(AuthenticationError):
            dm._headers(auth_required=True)


class TestClassifyTable:

    def test_material_table(self):
        assert DataManager._classify_table("anode_materials") == "materials"

    def test_cell_table(self):
        assert DataManager._classify_table("cell_references") == "cells"

    def test_unknown_table_raises(self):
        with pytest.raises(ValueError):
            DataManager._classify_table("unknown_table")


class TestParseCondition:

    def test_standard_condition(self):
        field, value = DataManager._parse_condition("name = 'LFP'")
        assert field == "name"
        assert value == "LFP"

    def test_spaces_around_equals(self):
        field, value = DataManager._parse_condition("name='Test Cell'")
        assert field == "name"
        assert value == "Test Cell"

    def test_invalid_condition_raises(self):
        with pytest.raises(ValueError):
            DataManager._parse_condition("invalid condition")


class TestGetTableNames:

    def test_returns_sorted_list(self, dm):
        names = dm.get_table_names()
        assert names == sorted(_TEST_MATERIAL_TABLES | _TEST_CELL_TABLES)
        assert isinstance(names, list)


class TestRequestErrorHandling:

    def _mock_response(self, status_code, json_data=None, text=""):
        resp = MagicMock()
        resp.status_code = status_code
        resp.text = text
        resp.json.return_value = json_data or {}
        resp.content = b""
        return resp

    def test_401_raises_auth_error(self, dm):
        dm._session.request.return_value = self._mock_response(401)
        with pytest.raises(AuthenticationError):
            dm._request("GET", "/test")

    def test_403_raises_forbidden(self, dm):
        dm._session.request.return_value = self._mock_response(403, {"error": "nope"})
        with pytest.raises(ForbiddenError):
            dm._request("GET", "/test")

    def test_404_raises_not_found(self, dm):
        dm._session.request.return_value = self._mock_response(404, {"error": "gone"})
        with pytest.raises(NotFoundError):
            dm._request("GET", "/test")

    def test_409_raises_conflict(self, dm):
        dm._session.request.return_value = self._mock_response(409, {"error": "dup"})
        with pytest.raises(ConflictError):
            dm._request("GET", "/test")

    def test_500_raises_api_error(self, dm):
        dm._session.request.return_value = self._mock_response(500, text="Internal error")
        with pytest.raises(APIError):
            dm._request("GET", "/test")

    def test_204_returns_none(self, dm):
        dm._session.request.return_value = self._mock_response(204)
        assert dm._request("DELETE", "/test") is None


class TestIsDevelopment:

    def test_production_by_default(self, monkeypatch):
        monkeypatch.delenv("OPENCELL_ENV", raising=False)
        from steer_core.Data import is_development
        assert is_development() is False

    def test_development_mode(self, monkeypatch):
        monkeypatch.setenv("OPENCELL_ENV", "development")
        from steer_core.Data import is_development
        assert is_development() is True

    def test_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("OPENCELL_ENV", "Development")
        from steer_core.Data import is_development
        assert is_development() is True
