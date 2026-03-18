# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Utils.CurveComposition — generic paired curve composition."""

import numpy as np
import pytest

from steer_core.Utils.CurveComposition import (
    build_zero_value_proxy,
    compute_paired_curve_difference,
    DEFAULT_INTERPOLATION_POINTS,
)


def _make_curve(primary_x, primary_y, secondary_x, secondary_y):
    """Helper to build a [x, y, direction] curve from segment arrays."""
    n_p = len(primary_x)
    n_s = len(secondary_x)
    curve = np.empty((n_p + n_s, 3))
    curve[:n_p, 0] = primary_x
    curve[:n_p, 1] = primary_y
    curve[:n_p, 2] = 1
    curve[n_p:, 0] = secondary_x
    curve[n_p:, 1] = secondary_y
    curve[n_p:, 2] = -1
    return curve


class TestBuildZeroValueProxy:

    def test_output_shape(self):
        ref = _make_curve([0, 5, 10], [1, 2, 3], [10, 5, 0], [3, 2, 1])
        proxy = build_zero_value_proxy(ref, n_points=50)
        assert proxy.shape == (100, 3)

    def test_all_y_values_zero(self):
        ref = _make_curve([0, 5, 10], [1, 2, 3], [10, 5, 0], [3, 2, 1])
        proxy = build_zero_value_proxy(ref, n_points=50)
        np.testing.assert_array_equal(proxy[:, 1], 0.0)

    def test_x_range_matches_reference(self):
        ref = _make_curve([2, 5, 8], [1, 2, 3], [8, 5, 2], [3, 2, 1])
        proxy = build_zero_value_proxy(ref, n_points=50)
        primary = proxy[proxy[:, 2] == 1]
        secondary = proxy[proxy[:, 2] == -1]
        assert primary[:, 0].min() == pytest.approx(2.0)
        assert primary[:, 0].max() == pytest.approx(8.0)
        assert secondary[:, 0].min() == pytest.approx(2.0)
        assert secondary[:, 0].max() == pytest.approx(8.0)

    def test_direction_labels(self):
        ref = _make_curve([0, 10], [1, 2], [10, 0], [2, 1])
        proxy = build_zero_value_proxy(ref, n_points=20)
        assert len(proxy[proxy[:, 2] == 1]) == 20
        assert len(proxy[proxy[:, 2] == -1]) == 20

    def test_default_n_points(self):
        ref = _make_curve([0, 10], [1, 2], [10, 0], [2, 1])
        proxy = build_zero_value_proxy(ref)
        assert proxy.shape == (2 * DEFAULT_INTERPOLATION_POINTS, 3)


class TestComputePairedCurveDifference:

    def test_output_shape(self):
        a = _make_curve(
            np.linspace(0, 10, 20), np.linspace(1, 4, 20),
            np.linspace(10, 0, 20), np.linspace(4, 1, 20),
        )
        b = _make_curve(
            np.linspace(0, 12, 20), np.linspace(0, 0.5, 20),
            np.linspace(12, 0, 20), np.linspace(0.5, 0, 20),
        )
        ratio, combined = compute_paired_curve_difference(a, b, n_points=50)
        assert combined.shape == (100, 3)

    def test_ratio_computation(self):
        a = _make_curve([0, 5, 10], [1, 2, 3], [10, 5, 0], [3, 2, 1])
        b = _make_curve([0, 6, 12], [0, 0.5, 1], [12, 6, 0], [1, 0.5, 0])
        ratio, _ = compute_paired_curve_difference(a, b, n_points=50)
        assert ratio == pytest.approx(12.0 / 10.0)

    def test_difference_with_zero_proxy(self):
        a = _make_curve(
            np.linspace(0, 10, 50), np.linspace(2, 4, 50),
            np.linspace(10, 0, 50), np.linspace(4, 2, 50),
        )
        b = _make_curve(
            np.linspace(0, 10, 50), np.zeros(50),
            np.linspace(10, 0, 50), np.zeros(50),
        )
        _, combined = compute_paired_curve_difference(a, b, n_points=50)
        primary = combined[combined[:, 2] == 1]
        # With b=0, combined y should ≈ a's y
        assert primary[:, 1].mean() == pytest.approx(3.0, abs=0.2)

    def test_direction_labels_preserved(self):
        a = _make_curve([0, 10], [1, 3], [10, 0], [3, 1])
        b = _make_curve([0, 10], [0, 0], [10, 0], [0, 0])
        _, combined = compute_paired_curve_difference(a, b, n_points=20)
        assert len(combined[combined[:, 2] == 1]) == 20
        assert len(combined[combined[:, 2] == -1]) == 20

    def test_secondary_segment_reversed(self):
        a = _make_curve(
            np.linspace(0, 10, 20), np.linspace(1, 3, 20),
            np.linspace(10, 0, 20), np.linspace(3, 1, 20),
        )
        b = _make_curve(
            np.linspace(0, 10, 20), np.zeros(20),
            np.linspace(10, 0, 20), np.zeros(20),
        )
        _, combined = compute_paired_curve_difference(a, b, n_points=20)
        secondary = combined[combined[:, 2] == -1]
        # Secondary x should be in descending order (reversed)
        assert secondary[0, 0] > secondary[-1, 0]
