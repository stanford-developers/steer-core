# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Constants modules."""

import math

from steer_core.Constants import Format, Units, Universal


class TestFormat:
    """Tests for Format constants."""

    def test_hour_format_string(self):
        assert Format.DEFAULT_HOUR_FMT == "%Y-%m-%d-%H"

    def test_day_format_string(self):
        assert Format.DEFAULT_DAY_FMT == "%Y-%m-%d"

    def test_formats_are_strings(self):
        assert isinstance(Format.DEFAULT_HOUR_FMT, str)
        assert isinstance(Format.DEFAULT_DAY_FMT, str)


class TestUnits:
    """Tests for unit conversion constants."""

    def test_mass_conversions_are_inverses(self):
        assert Units.KG_TO_G * Units.G_TO_KG == pytest.approx(1.0)
        assert Units.M_TO_MM * Units.MM_TO_M == pytest.approx(1.0)
        assert Units.M_TO_CM * Units.CM_TO_M == pytest.approx(1.0)

    def test_time_conversions_are_inverses(self):
        assert Units.S_TO_H * Units.H_TO_S == pytest.approx(1.0)
        assert Units.S_TO_MIN * Units.MIN_TO_S == pytest.approx(1.0)

    def test_angle_conversion(self):
        assert Units.DEG_TO_RAD == pytest.approx(math.radians(1))

    def test_percent_fraction_conversions(self):
        assert Units.PERCENT_TO_FRACTION == pytest.approx(0.01)
        assert Units.FRACTION_TO_PERCENT == pytest.approx(100.0)

    def test_energy_conversion(self):
        assert Units.J_TO_WH == pytest.approx(1 / 3600)

    def test_volume_conversions(self):
        assert Units.L_TO_M3 * Units.M3_TO_L == pytest.approx(1.0)

    def test_current_conversions(self):
        assert Units.A_TO_mA * Units.mA_TO_A == pytest.approx(1.0)

    def test_all_constants_are_numeric(self):
        for name in dir(Units):
            if name.startswith("_"):
                continue
            val = getattr(Units, name)
            assert isinstance(val, (int, float)), f"{name} should be numeric"


class TestUniversal:
    """Tests for universal physical constants."""

    def test_pi(self):
        assert Universal.PI == pytest.approx(math.pi)

    def test_two_pi(self):
        assert Universal.TWO_PI == pytest.approx(2 * math.pi)

    def test_molar_masses_positive(self):
        assert Universal.MW_G_PER_MOL_NO2 > 0
        assert Universal.MW_G_PER_MOL_SO2 > 0
        assert Universal.MW_G_PER_MOL_CO2 > 0


# Need pytest.approx at module level for parametrized tests
import pytest
