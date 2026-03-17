# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Data.DataMixin."""

import numpy as np
import pytest

from steer_core.Mixins.Data import DataMixin


class TestEnforceMonotonicity:

    def test_already_increasing(self):
        arr = np.array([1.0, 2.0, 3.0, 4.0])
        result = DataMixin.enforce_monotonicity(arr)
        np.testing.assert_array_equal(result, arr)

    def test_already_decreasing(self):
        arr = np.array([4.0, 3.0, 2.0, 1.0])
        result = DataMixin.enforce_monotonicity(arr)
        np.testing.assert_array_equal(result, arr)

    def test_non_monotonic_ascending(self):
        arr = np.array([1.0, 3.0, 2.0, 4.0])
        result = DataMixin.enforce_monotonicity(arr)
        diffs = np.diff(result)
        assert np.all(diffs >= 0), "Result should be monotonically increasing"

    def test_non_monotonic_descending(self):
        arr = np.array([4.0, 2.0, 3.0, 1.0])
        result = DataMixin.enforce_monotonicity(arr)
        diffs = np.diff(result)
        assert np.all(diffs <= 0), "Result should be monotonically decreasing"

    def test_preserves_endpoints(self):
        arr = np.array([0.0, 5.0, 3.0, 10.0])
        result = DataMixin.enforce_monotonicity(arr)
        assert result[0] == pytest.approx(arr[0], abs=1e-6)
        assert result[-1] == pytest.approx(arr[-1], abs=1e-6)


class TestSumBreakdowns:

    def test_simple_breakdown(self):
        class Component:
            def __init__(self, breakdown):
                self._mass_breakdown = breakdown

        c1 = Component({"material": 5.0, "binder": 1.0})
        c2 = Component({"material": 3.0, "binder": 2.0})
        result = DataMixin.sum_breakdowns([c1, c2], "mass")
        assert result["material"] == pytest.approx(8.0)
        assert result["binder"] == pytest.approx(3.0)

    def test_nested_breakdown(self):
        class Component:
            def __init__(self, breakdown):
                self._mass_breakdown = breakdown

        c1 = Component({"layer": {"top": 1.0, "bottom": 2.0}})
        c2 = Component({"layer": {"top": 3.0, "bottom": 4.0}})
        result = DataMixin.sum_breakdowns([c1, c2], "mass")
        assert result["layer"]["top"] == pytest.approx(4.0)
        assert result["layer"]["bottom"] == pytest.approx(6.0)

    def test_fallback_to_simple_attribute(self):
        class Simple:
            def __init__(self, mass):
                self._mass = mass

        c1 = Simple(5.0)
        c2 = Simple(3.0)
        result = DataMixin.sum_breakdowns([c1, c2], "mass")
        assert result == pytest.approx(8.0)

    def test_mixed_breakdown_and_simple(self):
        class WithBreakdown:
            def __init__(self):
                self._mass_breakdown = {"material": 5.0}

        class WithSimple:
            def __init__(self):
                self._mass = 3.0

        result = DataMixin.sum_breakdowns(
            [WithBreakdown(), WithSimple()], "mass"
        )
        assert isinstance(result, dict)
        assert result["material"] == pytest.approx(5.0)
        assert result["total_mass"] == pytest.approx(3.0)

    def test_empty_components(self):
        result = DataMixin.sum_breakdowns([], "mass")
        assert result == 0

    def test_none_breakdown_ignored(self):
        class Component:
            def __init__(self):
                self._mass_breakdown = None

        result = DataMixin.sum_breakdowns([Component()], "mass")
        assert result == 0
