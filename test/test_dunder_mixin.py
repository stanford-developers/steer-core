# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Dunder.DunderMixin."""

import numpy as np
import pytest

from conftest import SampleObject


class TestDunderEquality:
    """Tests for __eq__ via SampleObject."""

    def test_identity(self, sample_obj):
        assert sample_obj == sample_obj

    def test_equal_objects(self, sample_obj):
        other = SampleObject(name="test", value=1.0)
        assert sample_obj == other

    def test_different_values(self, sample_obj):
        other = SampleObject(name="test", value=99.0)
        assert sample_obj != other

    def test_different_type(self, sample_obj):
        assert sample_obj != "not an object"

    def test_different_name(self, sample_obj):
        other = SampleObject(name="different", value=1.0)
        assert sample_obj != other


class TestDunderHash:

    def test_hash_is_identity_based(self, sample_obj):
        assert hash(sample_obj) == hash(id(sample_obj))

    def test_different_objects_different_hash(self, sample_obj):
        other = SampleObject()
        assert hash(sample_obj) != hash(other)


class TestDunderStr:

    def test_str_with_name(self, sample_obj):
        result = str(sample_obj)
        assert "SampleObject" in result
        assert "test" in result

    def test_str_without_name(self):
        obj = SampleObject(name="", value=1.0)
        result = str(obj)
        assert "SampleObject" in result

    def test_repr_matches_str(self, sample_obj):
        assert repr(sample_obj) == str(sample_obj)


class TestPropertyExclusion:

    def test_trace_property_excluded(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._should_exclude_property_static("some_trace") is True

    def test_range_property_excluded(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._should_exclude_property_static("some_range") is True

    def test_last_updated_excluded(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._should_exclude_property_static("last_updated") is True

    def test_regular_property_not_excluded(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._should_exclude_property_static("mass") is False

    def test_datum_excluded_from_viewable_stats(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._should_exclude_property_viewable_stat_static("datum_x") is True


class TestIsNumericAnnotation:

    def test_float(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._is_numeric_annotation(float) is True

    def test_int(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._is_numeric_annotation(int) is True

    def test_str(self):
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._is_numeric_annotation(str) is False

    def test_optional_float(self):
        import typing
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._is_numeric_annotation(typing.Optional[float]) is True

    def test_any_is_not_numeric(self):
        import typing
        from steer_core.Mixins.Dunder import DunderMixin
        assert DunderMixin._is_numeric_annotation(typing.Any) is False


class TestComparisonHelpers:

    def test_compare_none_both_none(self, sample_obj):
        cont, result = sample_obj._compare_none_values(None, None)
        assert cont is True
        assert result is True

    def test_compare_none_one_none(self, sample_obj):
        cont, result = sample_obj._compare_none_values(None, 5)
        assert cont is False
        assert result is False

    def test_compare_numpy_arrays_equal(self, sample_obj):
        a = np.array([1, 2, 3])
        b = np.array([1, 2, 3])
        cont, result = sample_obj._compare_numpy_arrays(a, b)
        assert cont is False
        assert result is True

    def test_compare_numpy_arrays_unequal(self, sample_obj):
        a = np.array([1, 2, 3])
        b = np.array([4, 5, 6])
        cont, result = sample_obj._compare_numpy_arrays(a, b)
        assert cont is False
        assert result is False

    def test_compare_dicts_equal(self, sample_obj):
        d1 = {"a": 1, "b": 2}
        d2 = {"a": 1, "b": 2}
        cont, result = sample_obj._compare_dictionaries(d1, d2)
        assert cont is False
        assert result is True

    def test_compare_dicts_unequal(self, sample_obj):
        d1 = {"a": 1}
        d2 = {"a": 2}
        cont, result = sample_obj._compare_dictionaries(d1, d2)
        assert cont is False
        assert result is False

    def test_compare_sequences(self, sample_obj):
        cont, result = sample_obj._compare_sequences([1, 2], [1, 2])
        assert cont is False
        assert result is True
