# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Utils.CurveProcessing — generic paired curve utilities."""

import numpy as np
import pytest

from steer_core.Utils.CurveProcessing import (
    correct_segment_directions,
    make_segments_monotonic,
    reverse_secondary_segment,
    prepend_primary_endpoint_to_secondary,
    scale_secondary_segment,
    scale_curve,
    interpolate_between_curves,
    interpolate_curve_at_target,
    prepare_arrays_for_interp,
    truncate_and_shift_segments,
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


class TestCorrectSegmentDirections:

    def test_no_swap_when_primary_has_larger_range(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [0, 3], [3, 1])
        result = correct_segment_directions(curve)
        primary = result[result[:, 2] == 1]
        assert primary[:, 0].max() - primary[:, 0].min() == pytest.approx(10.0)

    def test_swap_when_secondary_has_larger_range(self):
        curve = _make_curve([0, 2], [1, 2], [0, 5, 10], [3, 2, 1])
        result = correct_segment_directions(curve)
        # After swap, the wider segment should be primary
        primary = result[result[:, 2] == 1]
        assert primary[:, 0].max() - primary[:, 0].min() == pytest.approx(10.0)

    def test_returns_unchanged_if_one_segment_empty(self):
        curve = np.array([[0, 1, 1], [5, 2, 1], [10, 3, 1]])
        result = correct_segment_directions(curve)
        np.testing.assert_array_equal(result, curve)


class TestMakeSegmentsMonotonic:

    def test_already_monotonic(self):
        curve = _make_curve([1, 2, 3], [1, 2, 3], [1, 2, 3], [3, 2, 1])
        result = make_segments_monotonic(curve)
        primary = result[result[:, 2] == 1]
        assert np.all(np.diff(primary[:, 0]) >= 0)

    def test_non_monotonic_becomes_monotonic(self):
        curve = _make_curve([1, 3, 2, 4], [1, 3, 2, 4], [1, 2, 3, 4], [4, 3, 2, 1])
        result = make_segments_monotonic(curve)
        primary = result[result[:, 2] == 1]
        assert np.all(np.diff(primary[:, 0]) >= 0)
        assert np.all(np.diff(primary[:, 1]) >= 0)


class TestReverseSecondarySegment:

    def test_secondary_x_mirrors_from_max(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [0, 3, 6], [3, 2, 1])
        result = reverse_secondary_segment(curve)
        secondary = result[result[:, 2] == -1]
        # Original secondary x: [0,3,6], max_x=10 → reversed: [10, 7, 4]
        np.testing.assert_array_almost_equal(secondary[:, 0], [10, 7, 4])

    def test_primary_unchanged(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [0, 3, 6], [3, 2, 1])
        result = reverse_secondary_segment(curve)
        primary = result[result[:, 2] == 1]
        np.testing.assert_array_almost_equal(primary[:, 0], [0, 5, 10])


class TestPrependPrimaryEndpointToSecondary:

    def test_junction_point_added(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [8, 6, 4], [2.5, 2, 1.5])
        result = prepend_primary_endpoint_to_secondary(curve)
        secondary = result[result[:, 2] == -1]
        # First secondary point should be last primary point
        assert secondary[0, 0] == pytest.approx(10.0)
        assert secondary[0, 1] == pytest.approx(3.0)
        assert len(secondary) == 4  # was 3, now 4

    def test_primary_unchanged(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [8, 6, 4], [2.5, 2, 1.5])
        result = prepend_primary_endpoint_to_secondary(curve)
        primary = result[result[:, 2] == 1]
        assert len(primary) == 3


class TestScaleSecondarySegment:

    def test_scaling_factor_one_is_identity(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [10, 7, 4], [3, 2, 1])
        result = scale_secondary_segment(curve, 1.0)
        secondary = result[result[:, 2] == -1]
        np.testing.assert_array_almost_equal(secondary[:, 0], [10, 7, 4])

    def test_scaling_factor_two_doubles_distance_from_max(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [10, 8, 6], [3, 2, 1])
        result = scale_secondary_segment(curve, 2.0)
        secondary = result[result[:, 2] == -1]
        # distances from 10: [0, 2, 4] → scaled: [0, 4, 8] → values: [10, 6, 2]
        np.testing.assert_array_almost_equal(secondary[:, 0], [10, 6, 2])


class TestScaleCurve:

    def test_scales_all_x_values(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [10, 7, 4], [3, 2, 1])
        result = scale_curve(curve, 0.5)
        assert result[:, 0].max() == pytest.approx(5.0)

    def test_does_not_modify_input(self):
        curve = _make_curve([0, 5, 10], [1, 2, 3], [10, 7, 4], [3, 2, 1])
        original = curve.copy()
        scale_curve(curve, 0.5)
        np.testing.assert_array_equal(curve, original)


class TestInterpolateBetweenCurves:

    def test_equal_bounds_returns_copy(self):
        below = np.array([[0, 1, 1], [5, 2, 1], [10, 3, 1]])
        result = interpolate_between_curves(2.5, below, below, 3.0, 3.0)
        np.testing.assert_array_equal(result, below)

    def test_midpoint_interpolation(self):
        below = np.array([[0, 1, 1], [10, 2, 1]])
        above = np.array([[0, 2, 1], [10, 4, 1]])
        result = interpolate_between_curves(3.0, below, above, 2.0, 4.0, n_points=10)
        # At midpoint, y should be average of below and above
        assert result[:, 1].mean() == pytest.approx(
            (np.interp(result[:, 0], [0, 10], [1, 2]) +
             np.interp(result[:, 0], [0, 10], [2, 4])).mean() / 2,
            abs=0.1,
        )

    def test_secondary_segment_handled(self):
        below = np.array([[10, 3, -1], [5, 2, -1], [0, 1, -1]])
        above = np.array([[10, 4, -1], [5, 3, -1], [0, 2, -1]])
        result = interpolate_between_curves(3.5, below, above, 3.0, 4.0, n_points=10)
        assert result[0, 2] == -1


class TestInterpolateCurveAtTarget:

    def test_interpolates_between_two_curves(self):
        curve_low = _make_curve([0, 5, 10], [1, 1.5, 2], [10, 5, 0], [2, 1.5, 1])
        curve_high = _make_curve([0, 5, 10], [2, 3, 4], [10, 5, 0], [4, 3, 2])
        result = interpolate_curve_at_target([curve_low, curve_high], 3.0, n_points=50)
        assert result.shape[1] == 3
        # Both segments present
        assert len(result[result[:, 2] == 1]) > 0
        assert len(result[result[:, 2] == -1]) > 0


class TestPrepareArraysForInterp:

    def test_already_increasing(self):
        x = np.array([1, 2, 3, 4])
        y = np.array([10, 20, 30, 40])
        xr, yr = prepare_arrays_for_interp(x, y)
        np.testing.assert_array_equal(xr, x)
        np.testing.assert_array_equal(yr, y)

    def test_both_decreasing_flipped(self):
        x = np.array([4, 3, 2, 1])
        y = np.array([40, 30, 20, 10])
        xr, yr = prepare_arrays_for_interp(x, y)
        np.testing.assert_array_equal(xr, np.array([1, 2, 3, 4]))
        np.testing.assert_array_equal(yr, np.array([10, 20, 30, 40]))

    def test_x_decreasing_y_increasing_sorted(self):
        x = np.array([4, 3, 2, 1])
        y = np.array([10, 20, 30, 40])
        xr, yr = prepare_arrays_for_interp(x, y)
        assert np.all(np.diff(xr) >= 0)


class TestTruncateAndShiftSegments:

    def test_truncate_below_cutoff(self):
        # Primary segment: y goes 1→3, secondary: y goes 3→1
        curve = _make_curve(
            [0, 5, 10], [1.0, 2.0, 3.0],
            [10, 5, 0], [3.0, 2.0, 1.0],
        )
        result = truncate_and_shift_segments([curve], 2.5, truncate_below_cutoff=True)
        # All y-values should be <= 2.5
        assert result[:, 1].max() <= 2.5 + 1e-10

    def test_truncate_above_cutoff(self):
        curve = _make_curve(
            [0, 5, 10], [1.0, 2.0, 3.0],
            [10, 5, 0], [3.0, 2.0, 1.0],
        )
        result = truncate_and_shift_segments([curve], 1.5, truncate_below_cutoff=False)
        # All y-values should be >= 1.5
        assert result[:, 1].min() >= 1.5 - 1e-10
