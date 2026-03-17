# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Utils."""

import numpy as np
import pytest

from steer_core.Utils import is_plotly_trace, round_dict_recursive


class TestIsPlotlyTrace:
    """Tests for is_plotly_trace utility."""

    def test_plotly_scatter_is_trace(self):
        import plotly.graph_objects as go
        assert is_plotly_trace(go.Scatter(x=[1], y=[1])) is True

    def test_plotly_bar_is_trace(self):
        import plotly.graph_objects as go
        assert is_plotly_trace(go.Bar(x=[1], y=[1])) is True

    def test_string_is_not_trace(self):
        assert is_plotly_trace("not a trace") is False

    def test_none_is_not_trace(self):
        assert is_plotly_trace(None) is False

    def test_dict_is_not_trace(self):
        assert is_plotly_trace({"type": "scatter"}) is False

    def test_numpy_array_is_not_trace(self):
        assert is_plotly_trace(np.array([1, 2, 3])) is False

    def test_object_without_module(self):
        class NoModule:
            def __getattribute__(self, name):
                if name == "__module__":
                    raise AttributeError
                return super().__getattribute__(name)
        assert is_plotly_trace(NoModule()) is False


class TestRoundDictRecursive:
    """Tests for round_dict_recursive utility."""

    def test_simple_float(self):
        assert round_dict_recursive(3.14159, precision=2) == pytest.approx(3.14)

    def test_flat_dict(self):
        result = round_dict_recursive({"a": 1.111, "b": 2.999}, precision=1)
        assert result == {"a": pytest.approx(1.1), "b": pytest.approx(3.0)}

    def test_nested_dict(self):
        data = {"outer": {"inner": 1.23456}}
        result = round_dict_recursive(data, precision=3)
        assert result["outer"]["inner"] == pytest.approx(1.235)

    def test_unit_conversion(self):
        result = round_dict_recursive(1.0, precision=2, unit_conversion=1000.0)
        assert result == pytest.approx(1000.0)

    def test_unit_conversion_with_dict(self):
        data = {"val": 0.001}
        result = round_dict_recursive(data, precision=2, unit_conversion=1000.0)
        assert result["val"] == pytest.approx(1.0)

    def test_integer_input(self):
        assert round_dict_recursive(5, precision=2) == pytest.approx(5.0)

    def test_empty_dict(self):
        assert round_dict_recursive({}) == {}
