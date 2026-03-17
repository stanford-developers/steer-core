# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.DateTime.DateTimeMixin."""

from datetime import datetime

import pytest

from steer_core.Mixins.DateTime import DateTimeMixin


class TestStrToDatetime:

    def test_hour_format(self):
        result = DateTimeMixin.str_to_datetime("2024-01-15-14")
        assert result == datetime(2024, 1, 15, 14, 0, 0)

    def test_day_format(self):
        result = DateTimeMixin.str_to_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15, 0, 0, 0)

    def test_explicit_format(self):
        result = DateTimeMixin.str_to_datetime("15/01/2024", fmt="%d/%m/%Y")
        assert result == datetime(2024, 1, 15)

    def test_non_string_raises_type_error(self):
        with pytest.raises(TypeError):
            DateTimeMixin.str_to_datetime(12345)

    def test_invalid_format_raises_value_error(self):
        with pytest.raises(ValueError):
            DateTimeMixin.str_to_datetime("not-a-date")

    def test_wrong_explicit_format_raises(self):
        with pytest.raises(ValueError):
            DateTimeMixin.str_to_datetime("2024-01-15", fmt="%d/%m/%Y")


class TestDatetimeToStr:

    def test_default_hour_format(self):
        dt = datetime(2024, 1, 15, 14)
        assert DateTimeMixin.datetime_to_str(dt) == "2024-01-15-14"

    def test_midnight_shows_zero_hour(self):
        dt = datetime(2024, 1, 15, 0)
        assert DateTimeMixin.datetime_to_str(dt) == "2024-01-15-00"

    def test_explicit_format(self):
        dt = datetime(2024, 1, 15)
        assert DateTimeMixin.datetime_to_str(dt, fmt="%Y-%m-%d") == "2024-01-15"

    def test_non_datetime_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.datetime_to_str("2024-01-15")


class TestShiftYears:

    def test_shift_forward(self):
        dt = datetime(2024, 6, 15, 12)
        result = DateTimeMixin.shift_years(dt, 2)
        assert result == datetime(2026, 6, 15, 12)

    def test_shift_backward(self):
        dt = datetime(2026, 3, 1)
        result = DateTimeMixin.shift_years(dt, -2)
        assert result == datetime(2024, 3, 1)

    def test_leap_day_to_non_leap_year(self):
        dt = datetime(2024, 2, 29, 12)
        result = DateTimeMixin.shift_years(dt, 1)
        assert result == datetime(2025, 2, 28, 12)

    def test_non_datetime_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.shift_years("2024-01-01", 1)

    def test_non_int_years_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.shift_years(datetime(2024, 1, 1), 1.5)


class TestShiftMonths:

    def test_shift_forward(self):
        dt = datetime(2024, 1, 15, 14)
        result = DateTimeMixin.shift_months(dt, 2)
        assert result == datetime(2024, 3, 15, 14)

    def test_shift_backward(self):
        dt = datetime(2024, 3, 15)
        result = DateTimeMixin.shift_months(dt, -2)
        assert result == datetime(2024, 1, 15)

    def test_end_of_month_clamping(self):
        dt = datetime(2024, 1, 31)
        result = DateTimeMixin.shift_months(dt, 1)
        assert result == datetime(2024, 2, 29)  # 2024 is leap year

    def test_cross_year_boundary(self):
        dt = datetime(2024, 11, 15)
        result = DateTimeMixin.shift_months(dt, 3)
        assert result == datetime(2025, 2, 15)

    def test_negative_cross_year_boundary(self):
        dt = datetime(2024, 2, 15)
        result = DateTimeMixin.shift_months(dt, -3)
        assert result == datetime(2023, 11, 15)

    def test_non_datetime_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.shift_months("2024-01-01", 1)

    def test_non_int_months_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.shift_months(datetime(2024, 1, 1), 1.5)


class TestValidateEndAfterStart:

    def test_valid_strictly(self):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 2)
        DateTimeMixin.validate_end_after_start(start, end)  # Should not raise

    def test_equal_strictly_raises(self):
        dt = datetime(2024, 1, 1)
        with pytest.raises(ValueError):
            DateTimeMixin.validate_end_after_start(dt, dt)

    def test_equal_non_strictly_ok(self):
        dt = datetime(2024, 1, 1)
        DateTimeMixin.validate_end_after_start(dt, dt, strictly=False)

    def test_end_before_start_raises(self):
        start = datetime(2024, 1, 2)
        end = datetime(2024, 1, 1)
        with pytest.raises(ValueError):
            DateTimeMixin.validate_end_after_start(start, end)

    def test_non_datetime_start_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.validate_end_after_start("2024-01-01", datetime(2024, 1, 2))

    def test_non_datetime_end_raises(self):
        with pytest.raises(TypeError):
            DateTimeMixin.validate_end_after_start(datetime(2024, 1, 1), "2024-01-02")
