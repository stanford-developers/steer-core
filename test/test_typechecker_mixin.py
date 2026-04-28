# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.TypeChecker.ValidationMixin (beyond plotly trace tests)."""

from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd
import pytest

from steer_core.Mixins.TypeChecker import ValidationMixin


class TestValidateType:

    def test_valid_single_type(self):
        ValidationMixin.validate_type(5, int, "count")

    def test_valid_multiple_types_tuple(self):
        ValidationMixin.validate_type(5, (int, float), "count")

    def test_valid_multiple_types_list(self):
        ValidationMixin.validate_type(5, [int, float], "count")

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError, match="count"):
            ValidationMixin.validate_type("x", int, "count")


class TestValidatePercentage:

    def test_valid_percentage(self):
        ValidationMixin.validate_percentage(50, "pct")

    def test_zero(self):
        ValidationMixin.validate_percentage(0, "pct")

    def test_hundred(self):
        ValidationMixin.validate_percentage(100, "pct")

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_percentage(-1, "pct")

    def test_over_hundred_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_percentage(101, "pct")

    def test_non_numeric_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_percentage("50", "pct")


class TestValidateFraction:

    def test_valid(self):
        ValidationMixin.validate_fraction(0.5, "frac")

    def test_zero(self):
        ValidationMixin.validate_fraction(0, "frac")

    def test_one(self):
        ValidationMixin.validate_fraction(1, "frac")

    def test_over_one_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_fraction(1.5, "frac")


class TestValidatePandasDataframe:

    def test_valid_dataframe(self):
        df = pd.DataFrame({"a": [1]})
        ValidationMixin.validate_pandas_dataframe(df, "df")

    def test_non_dataframe_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_pandas_dataframe([1, 2], "df")

    def test_missing_columns_raises(self):
        df = pd.DataFrame({"a": [1]})
        with pytest.raises(ValueError, match="missing"):
            ValidationMixin.validate_pandas_dataframe(df, "df", column_names=["a", "b"])


class TestValidateDatum:

    def test_valid_tuple(self):
        ValidationMixin.validate_datum((1.0, 2.0, 3.0))

    def test_valid_list(self):
        ValidationMixin.validate_datum([1, 2, 3])

    def test_valid_numpy(self):
        ValidationMixin.validate_datum(np.array([1.0, 2.0, 3.0]))

    def test_wrong_length_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_datum((1, 2))

    def test_non_numeric_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_datum(("a", "b", "c"))


class TestValidatePositiveFloat:

    def test_valid(self):
        ValidationMixin.validate_positive_float(5.0, "val")

    def test_zero(self):
        ValidationMixin.validate_positive_float(0, "val")

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_positive_float(-1.0, "val")

    def test_non_numeric_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_positive_float("5", "val")

    def test_numpy_int64(self):
        ValidationMixin.validate_positive_float(np.int64(5), "val")


class TestValidatePositiveInt:

    def test_valid(self):
        ValidationMixin.validate_positive_int(5, "n")

    def test_zero_strict_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_positive_int(0, "n")

    def test_zero_non_strict_ok(self):
        ValidationMixin.validate_positive_int(0, "n", strictly=False)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_positive_int(-1, "n")

    def test_bool_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_positive_int(True, "flag")

    def test_float_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_positive_int(5.0, "n")


class TestValidateString:

    def test_valid(self):
        ValidationMixin.validate_string("hello", "s")

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_string(123, "s")


class TestValidateTwoIterableOfFloats:

    def test_valid_tuple(self):
        ValidationMixin.validate_two_iterable_of_floats((1.0, 2.0), "dims")

    def test_valid_list(self):
        ValidationMixin.validate_two_iterable_of_floats([1, 2], "dims")

    def test_wrong_length_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_two_iterable_of_floats((1,), "dims")

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_two_iterable_of_floats((-1, 2), "dims")

    def test_non_numeric_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_two_iterable_of_floats(("a", "b"), "dims")


class TestValidatePositiveFloatList:

    def test_valid(self):
        ValidationMixin.validate_positive_float_list([1.0, 2.0], "vals")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_positive_float_list([], "vals")

    def test_negative_in_list_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_positive_float_list([1.0, -1.0], "vals")


class TestValidateEnumString:

    def test_valid(self):
        class Shape(Enum):
            CIRCLE = "circle"
            SQUARE = "square"

        ValidationMixin.validate_enum_string("circle", Shape, "shape")

    def test_invalid_raises(self):
        class Shape(Enum):
            CIRCLE = "circle"

        with pytest.raises(ValueError):
            ValidationMixin.validate_enum_string("triangle", Shape, "shape")

    def test_non_string_raises(self):
        class Shape(Enum):
            CIRCLE = "circle"

        with pytest.raises(TypeError):
            ValidationMixin.validate_enum_string(123, Shape, "shape")


class TestValidateDatetimeString:

    def test_hour_format(self):
        ValidationMixin.validate_datetime_string("2024-01-15-14", "dt")

    def test_day_format(self):
        ValidationMixin.validate_datetime_string("2024-01-15", "dt")

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            ValidationMixin.validate_datetime_string("2024/01/15", "dt")

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_datetime_string(12345, "dt")


class TestValidateNumber:

    def test_int(self):
        ValidationMixin.validate_number(42, "amount")

    def test_float(self):
        ValidationMixin.validate_number(3.14, "amount")

    def test_bool_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_number(True, "amount")

    def test_string_raises(self):
        with pytest.raises(TypeError):
            ValidationMixin.validate_number("100", "amount")


class TestValidateNotNone:

    def test_non_none_passes(self):
        ValidationMixin.validate_not_none(42, "rate")

    def test_zero_passes(self):
        ValidationMixin.validate_not_none(0, "rate")

    def test_empty_string_passes(self):
        ValidationMixin.validate_not_none("", "rate")

    def test_none_raises(self):
        with pytest.raises(ValueError, match="must not be None"):
            ValidationMixin.validate_not_none(None, "rate")


class TestValidateActiveMode:

    def test_matching_mode_passes(self):
        ValidationMixin.validate_active_mode("real", "real", "real_npv")

    def test_matching_enum_passes(self):
        from enum import Enum
        class Mode(str, Enum):
            REAL = "real"
            NOMINAL = "nominal"
        ValidationMixin.validate_active_mode(Mode.REAL, Mode.REAL, "real_npv")

    def test_mismatched_mode_raises(self):
        with pytest.raises(RuntimeError, match="not available in 'real' mode"):
            ValidationMixin.validate_active_mode("real", "nominal", "nominal_npv")

    def test_error_message_contains_property_name(self):
        with pytest.raises(RuntimeError, match="'nominal_net_present_value'"):
            ValidationMixin.validate_active_mode("real", "nominal", "nominal_net_present_value")
