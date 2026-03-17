# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Coordinates.CoordinateMixin."""

import numpy as np
import pytest

from steer_core.Mixins.Coordinates import CoordinateMixin


class TestRotateCoordinates:

    def test_2d_rotation_90_degrees(self, sample_coords_2d):
        result = CoordinateMixin.rotate_coordinates(sample_coords_2d, "z", 90)
        # After 90° CCW rotation about origin: (1,0) → (0,1)
        assert result[1, 0] == pytest.approx(0.0, abs=1e-10)
        assert result[1, 1] == pytest.approx(1.0, abs=1e-10)

    def test_2d_rotation_360_returns_original(self, sample_coords_2d):
        result = CoordinateMixin.rotate_coordinates(sample_coords_2d, "z", 360)
        np.testing.assert_allclose(result, sample_coords_2d, atol=1e-10)

    def test_3d_rotation_z_axis(self, sample_coords_3d):
        result = CoordinateMixin.rotate_coordinates(sample_coords_3d, "z", 90)
        assert result.shape == (4, 3)

    def test_3d_rotation_x_axis(self, sample_coords_3d):
        result = CoordinateMixin.rotate_coordinates(sample_coords_3d, "x", 90)
        assert result.shape == (4, 3)

    def test_3d_rotation_y_axis(self, sample_coords_3d):
        result = CoordinateMixin.rotate_coordinates(sample_coords_3d, "y", 90)
        assert result.shape == (4, 3)

    def test_rotation_about_center(self, sample_coords_2d):
        center = (0.5, 0.5)
        result = CoordinateMixin.rotate_coordinates(sample_coords_2d, "z", 360, center)
        np.testing.assert_allclose(result, sample_coords_2d, atol=1e-10)

    def test_2d_invalid_axis_raises(self, sample_coords_2d):
        with pytest.raises(ValueError):
            CoordinateMixin.rotate_coordinates(sample_coords_2d, "x", 90)

    def test_invalid_center_length_raises(self, sample_coords_2d):
        with pytest.raises(ValueError):
            CoordinateMixin.rotate_coordinates(sample_coords_2d, "z", 90, (1, 2, 3))

    def test_invalid_shape_raises(self):
        bad = np.array([[1, 2, 3, 4]])
        with pytest.raises(ValueError):
            CoordinateMixin.rotate_coordinates(bad, "z", 90)


class TestGetXzCenterLine:

    def test_single_polygon(self, sample_coords_3d):
        result = CoordinateMixin.get_xz_center_line(sample_coords_3d)
        assert result.shape == (2, 2)

    def test_empty_coordinates(self):
        empty = np.array([]).reshape(0, 3)
        result = CoordinateMixin.get_xz_center_line(empty)
        assert result.shape == (0, 2)

    def test_multi_segment_with_nan(self):
        coords = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [np.nan, np.nan, np.nan],
            [5.0, 0.0, 5.0],
            [6.0, 0.0, 6.0],
        ])
        result = CoordinateMixin.get_xz_center_line(coords)
        # Should have 2 segments separated by NaN
        assert result.shape[1] == 2
        nan_rows = np.isnan(result[:, 0])
        assert np.any(nan_rows)


class TestGetRadiusOfPoints:

    def test_square_points(self):
        coords = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
        ])
        radius, center = CoordinateMixin.get_radius_of_points(coords)
        assert radius > 0
        assert center[0] == pytest.approx(0.5, abs=0.1)
        assert center[1] == pytest.approx(0.5, abs=0.1)

    def test_insufficient_points_raises(self):
        coords = np.array([[0.0, 0.0], [1.0, 1.0]])
        with pytest.raises(ValueError):
            CoordinateMixin.get_radius_of_points(coords)


class TestCalculateSegmentCenterLine:

    def test_basic(self):
        x = np.array([0.0, 1.0, 2.0])
        z = np.array([1.0, 2.0, 3.0])
        result = CoordinateMixin._calculate_segment_center_line(x, z)
        assert result[0, 0] == pytest.approx(0.0)  # min_x
        assert result[1, 0] == pytest.approx(2.0)  # max_x
        assert result[0, 1] == pytest.approx(2.0)  # mean_z
