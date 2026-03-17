# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Datum.DatumMixin."""

import numpy as np
import pytest

from steer_core.Constants.Units import M_TO_MM, MM_TO_M


class TestDatumMixin:
    """Tests using the SampleObject from conftest that includes DatumMixin."""

    def test_default_datum(self, sample_obj):
        assert sample_obj.datum == (0.0, 0.0, 0.0)

    def test_set_and_get_datum_mm(self, sample_obj):
        sample_obj.datum = (10.0, 20.0, 30.0)
        result = sample_obj.datum
        assert result[0] == pytest.approx(10.0)
        assert result[1] == pytest.approx(20.0)
        assert result[2] == pytest.approx(30.0)

    def test_internal_storage_is_meters(self, sample_obj):
        sample_obj.datum = (1000.0, 0.0, 0.0)  # 1000 mm
        assert sample_obj._datum[0] == pytest.approx(1.0)  # 1.0 m

    def test_datum_x_property(self, sample_obj):
        sample_obj.datum = (5.0, 10.0, 15.0)
        assert sample_obj.datum_x == pytest.approx(5.0)

    def test_datum_y_property(self, sample_obj):
        sample_obj.datum = (5.0, 10.0, 15.0)
        assert sample_obj.datum_y == pytest.approx(10.0)

    def test_datum_z_property(self, sample_obj):
        sample_obj.datum = (5.0, 10.0, 15.0)
        assert sample_obj.datum_z == pytest.approx(15.0)

    def test_set_datum_x(self, sample_obj):
        sample_obj.datum = (0.0, 10.0, 20.0)
        sample_obj.datum_x = 99.0
        assert sample_obj.datum_x == pytest.approx(99.0)
        assert sample_obj.datum_y == pytest.approx(10.0)

    def test_set_datum_y(self, sample_obj):
        sample_obj.datum = (10.0, 0.0, 20.0)
        sample_obj.datum_y = 99.0
        assert sample_obj.datum_y == pytest.approx(99.0)
        assert sample_obj.datum_x == pytest.approx(10.0)

    def test_set_datum_z(self, sample_obj):
        sample_obj.datum = (10.0, 20.0, 0.0)
        sample_obj.datum_z = 99.0
        assert sample_obj.datum_z == pytest.approx(99.0)

    def test_ensure_datum_exists_initializes(self, sample_obj):
        del sample_obj._datum
        # Accessing datum should auto-initialize
        assert sample_obj.datum == (0.0, 0.0, 0.0)

    def test_compute_datum_translation(self, sample_obj):
        sample_obj.datum = (100.0, 200.0, 300.0)
        translation = sample_obj._compute_datum_translation((200.0, 200.0, 300.0))
        assert translation[0] == pytest.approx(0.1)  # 100mm = 0.1m
        assert translation[1] == pytest.approx(0.0)
        assert translation[2] == pytest.approx(0.0)

    def test_compute_datum_translation_no_existing(self, sample_obj):
        sample_obj._datum = None
        translation = sample_obj._compute_datum_translation((100.0, 200.0, 300.0))
        assert translation == (0.0, 0.0, 0.0)

    def test_datum_validation(self, sample_obj):
        with pytest.raises(ValueError):
            sample_obj.datum = (1.0, 2.0)  # Only 2 coordinates

    def test_datum_validation_non_numeric(self, sample_obj):
        with pytest.raises(TypeError):
            sample_obj.datum = ("a", "b", "c")
