# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Serializer.SerializerMixin."""

from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd
import pytest

from steer_core.Mixins.Serializer import SerializerMixin


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class SimpleSerializable(SerializerMixin):
    """Minimal class for serialization tests."""

    def __init__(self, name="test", value=42.0, tags=None):
        self._name = name
        self._value = value
        self._tags = tags or []

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


class TestSerializeDeserialize:

    def test_round_trip_basic(self):
        obj = SimpleSerializable("hello", 3.14, ["a", "b"])
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._name == "hello"
        assert restored._value == pytest.approx(3.14)
        assert restored._tags == ["a", "b"]

    def test_round_trip_no_compression(self):
        obj = SimpleSerializable("test", 1.0)
        data = obj.serialize(compress=False)
        restored = SimpleSerializable.deserialize(data)
        assert restored._name == "test"

    def test_round_trip_numpy_array(self):
        obj = SimpleSerializable()
        obj._array = np.array([1.0, 2.0, 3.0])
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        np.testing.assert_array_equal(restored._array, obj._array)

    def test_round_trip_datetime(self):
        obj = SimpleSerializable()
        obj._timestamp = datetime(2024, 1, 15, 14, 30)
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._timestamp == datetime(2024, 1, 15, 14, 30)

    def test_round_trip_tuple(self):
        obj = SimpleSerializable()
        obj._coords = (1.0, 2.0, 3.0)
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._coords == (1.0, 2.0, 3.0)

    def test_round_trip_nested_dict(self):
        obj = SimpleSerializable()
        obj._meta = {"layer": {"top": 1.0, "bottom": 2.0}}
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._meta == {"layer": {"top": 1.0, "bottom": 2.0}}

    def test_round_trip_dataframe(self):
        obj = SimpleSerializable()
        obj._df = pd.DataFrame({"x": [1, 2, 3], "y": [4.0, 5.0, 6.0]})
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        pd.testing.assert_frame_equal(
            restored._df.reset_index(drop=True),
            obj._df.reset_index(drop=True),
            check_dtype=False,
        )

    def test_round_trip_enum(self):
        obj = SimpleSerializable()
        obj._color = Color.RED
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._color == Color.RED

    def test_round_trip_none_values(self):
        obj = SimpleSerializable()
        obj._optional = None
        data = obj.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._optional is None


class TestSerializeNestedObjects:

    def test_nested_serializable(self):
        inner = SimpleSerializable("inner", 1.0)
        outer = SimpleSerializable("outer", 2.0)
        outer._child = inner
        data = outer.serialize()
        restored = SimpleSerializable.deserialize(data)
        assert restored._child._name == "inner"
        assert restored._child._value == pytest.approx(1.0)


class TestCompressionMarkers:

    def test_lz4_marker(self):
        obj = SimpleSerializable()
        data = obj.serialize(compress=True)
        assert data[0:1] == SerializerMixin._MARKER_LZ4

    def test_no_compression_marker(self):
        obj = SimpleSerializable()
        data = obj.serialize(compress=False)
        assert data[0:1] == SerializerMixin._MARKER_NONE


class TestSerializeValue:

    def test_primitive_passthrough(self):
        s = SimpleSerializable()
        assert s._serialize_value(42) == 42
        assert s._serialize_value("hello") == "hello"
        assert s._serialize_value(True) is True
        assert s._serialize_value(None) is None

    def test_callable_without_to_dict_returns_none(self):
        s = SimpleSerializable()
        assert s._serialize_value(lambda x: x) is None

    def test_list_serialization(self):
        s = SimpleSerializable()
        result = s._serialize_value([1, "two", 3.0])
        assert result == [1, "two", 3.0]
