# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Serializer.SerializerMixin."""

from datetime import datetime
from enum import Enum

import msgpack
import numpy as np
import pandas as pd
import pytest

from steer_core.Mixins import Serializer
from steer_core.Mixins.Propagation import PropagationMixin
from steer_core.Mixins.Serializer import (
    MissingClassError,
    SchemaVersionError,
    SerializerMixin,
    UnsafeClassPathError,
    allow_class_roots,
    register_class_alias,
)

# Deserialization only reconstructs classes rooted in an allowlisted package (see
# Serializer._ALLOWED_CLASS_ROOTS). The fixtures below live in this test module,
# so register its own root — the same hook a downstream package uses for its own
# SerializerMixin subclasses.
allow_class_roots(__name__.split(".", 1)[0])


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


class TestUntrustedPayloadRejection:
    """Deserialization must not be a code-execution sink.

    ``deserialize`` resolves class paths taken *from the payload*, so an
    untrusted ``.ocd`` file would otherwise choose which module gets imported —
    and the ``__enum__`` branch *calls* the resolved object with a payload value,
    which reaches any importable callable. These tests pin the allowlist and the
    type checks that close that.
    """

    @staticmethod
    def _payload(obj_dict) -> bytes:
        """Pack ``obj_dict`` into an uncompressed serialized payload."""
        return SerializerMixin._MARKER_NONE + msgpack.packb(
            obj_dict, use_bin_type=True
        )

    def test_enum_branch_cannot_call_arbitrary_callable(self, tmp_path):
        """The classic gadget: ``{"__enum__": ..., "class": "os.system"}``."""
        marker = tmp_path / "pwned"
        payload = self._payload(
            {
                "_class": f"{__name__}.SimpleSerializable",
                "_name": {
                    "__enum__": True,
                    "class": "os.system",
                    "value": f"touch {marker}",
                },
            }
        )
        with pytest.raises(UnsafeClassPathError, match="outside the allowed packages"):
            SerializerMixin.deserialize(payload)
        assert not marker.exists(), "payload executed despite being rejected"

    def test_enum_branch_rejects_allowlisted_non_enum(self):
        """An allowlisted root is not enough — it must actually be an Enum."""
        payload = self._payload(
            {
                "_class": f"{__name__}.SimpleSerializable",
                "_name": {
                    "__enum__": True,
                    "class": f"{__name__}.SimpleSerializable",
                    "value": "anything",
                },
            }
        )
        with pytest.raises(UnsafeClassPathError, match="not an Enum subclass"):
            SerializerMixin.deserialize(payload)

    def test_top_level_class_outside_allowlist_is_rejected(self):
        payload = self._payload({"_class": "subprocess.Popen", "_name": "x"})
        with pytest.raises(UnsafeClassPathError, match="outside the allowed packages"):
            SerializerMixin.deserialize(payload)

    def test_nested_object_outside_allowlist_is_rejected(self):
        payload = self._payload(
            {
                "_class": f"{__name__}.SimpleSerializable",
                "_child": {"__object__": True, "_class": "subprocess.Popen"},
            }
        )
        with pytest.raises(UnsafeClassPathError, match="outside the allowed packages"):
            SerializerMixin.deserialize(payload)

    def test_object_branch_rejects_allowlisted_non_serializable(self):
        """An allowlisted class that is not a SerializerMixin has no _from_dict."""
        payload = self._payload({"_class": f"{__name__}.Color", "_name": "x"})
        with pytest.raises(UnsafeClassPathError, match="not a SerializerMixin"):
            SerializerMixin.deserialize(payload)

    def test_non_class_path_is_rejected(self):
        """A path resolving to a plain function, not a class."""
        payload = self._payload({"_class": "steer_core.Mixins.Serializer._get_class"})
        with pytest.raises(UnsafeClassPathError, match="not a class"):
            SerializerMixin.deserialize(payload)

    @pytest.mark.parametrize("class_path", ["", "os", "nodots", 42, None])
    def test_malformed_class_path_is_rejected(self, class_path):
        payload = self._payload({"_class": class_path})
        with pytest.raises(UnsafeClassPathError):
            SerializerMixin.deserialize(payload)

    def test_unsafe_error_is_a_value_error(self):
        """Callers that already catch ValueError around deserialize keep working."""
        assert issubclass(UnsafeClassPathError, ValueError)

    def test_allowlist_does_not_break_legitimate_round_trip(self):
        """The positive control for all of the above."""
        obj = SimpleSerializable("real", 1.5)
        obj._color = Color.BLUE
        restored = SimpleSerializable.deserialize(obj.serialize())
        assert restored._name == "real"
        assert restored._color is Color.BLUE


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


class Holder(SerializerMixin):
    """Holds one arbitrary value, to test how a value type round-trips."""

    def __init__(self, value=None):
        self.value = value


class ParentHolder(PropagationMixin, SerializerMixin):
    """A propagating object, to test that a class value is not given a parent."""

    def __init__(self, value=None):
        self._parent = None
        self._value = value


def _round_trip(value):
    return Holder.deserialize(Holder(value).serialize()).value


@pytest.fixture
def clean_aliases():
    """Restore the global alias table and class cache after a test."""
    aliases = dict(Serializer._CLASS_ALIASES)
    cache = dict(Serializer._module_cache)
    yield
    Serializer._CLASS_ALIASES.clear()
    Serializer._CLASS_ALIASES.update(aliases)
    Serializer._module_cache.clear()
    Serializer._module_cache.update(cache)


class TestTypeReferences:

    def test_type_value_round_trips_as_the_same_class(self):
        assert _round_trip(SimpleSerializable) is SimpleSerializable

    def test_type_is_stored_as_a_path_not_as_code(self):
        payload = Holder()._serialize_value(Color)
        assert payload == {'__type__': f"{Color.__module__}.Color"}

    def test_serializable_class_as_value_is_not_called(self):
        # A SerializerMixin subclass has _to_dict, but as a class it must stay a reference
        assert _round_trip([SimpleSerializable, Holder]) == [SimpleSerializable, Holder]

    def test_classes_as_dict_keys(self):
        labour = {SimpleSerializable: 1.5, Holder: 0.25}
        assert _round_trip(labour) == labour

    def test_tuple_and_enum_keys(self):
        value = {(1, 2): "a", Color.RED: "b"}
        assert _round_trip(value) == value

    def test_type_outside_allowlist_is_rejected_on_load(self):
        data = Holder(datetime).serialize()
        with pytest.raises(UnsafeClassPathError):
            Holder.deserialize(data)

    def test_class_value_does_not_get_a_parent(self):
        restored = ParentHolder.deserialize(ParentHolder(ParentHolder).serialize())
        assert restored._value is ParentHolder


class TestSets:

    def test_set_round_trip(self):
        value = {1, "two", Color.BLUE}
        restored = _round_trip(value)
        assert restored == value and type(restored) is set

    def test_frozenset_of_types_round_trip(self):
        value = frozenset({SimpleSerializable, Holder})
        restored = _round_trip(value)
        assert restored == value and type(restored) is frozenset

    def test_equal_sets_give_equal_payloads(self):
        first = Holder({"b", "a", "c"})._serialize_value({"b", "a", "c"})
        second = Holder()._serialize_value({"c", "a", "b"})
        assert first == second


class TestClassAliases:

    def test_old_path_loads_as_the_new_class(self, clean_aliases):
        old = f"{__name__}.OldName"
        register_class_alias(old, f"{__name__}.SimpleSerializable")
        assert Serializer._get_class(old) is SimpleSerializable

    def test_aliases_chain(self, clean_aliases):
        register_class_alias(f"{__name__}.A", f"{__name__}.B")
        register_class_alias(f"{__name__}.B", f"{__name__}.SimpleSerializable")
        assert Serializer._get_class(f"{__name__}.A") is SimpleSerializable

    def test_cycle_is_rejected(self, clean_aliases):
        register_class_alias(f"{__name__}.A", f"{__name__}.B")
        with pytest.raises(ValueError, match="cycle"):
            register_class_alias(f"{__name__}.B", f"{__name__}.A")

    def test_alias_target_is_still_allowlisted(self, clean_aliases):
        register_class_alias(f"{__name__}.Old", "os.system")
        with pytest.raises(UnsafeClassPathError):
            Serializer._get_class(f"{__name__}.Old")

    @pytest.mark.parametrize("path", ["", "nodot", None])
    def test_malformed_alias_is_rejected(self, path, clean_aliases):
        with pytest.raises(ValueError):
            register_class_alias(path, f"{__name__}.SimpleSerializable")

    def test_alias_replaces_a_cached_path(self, clean_aliases):
        path = f"{__name__}.SimpleSerializable"
        Serializer._get_class(path)
        register_class_alias(path, f"{__name__}.Holder")
        assert Serializer._get_class(path) is Holder


class TestMissingClass:

    def test_removed_class_names_the_path(self):
        with pytest.raises(MissingClassError, match="register_class_alias"):
            Serializer._get_class(f"{__name__}.RemovedClass")

    def test_removed_module(self):
        with pytest.raises(MissingClassError):
            Serializer._get_class(f"{__name__}.removed_module.RemovedClass")

    def test_missing_class_is_a_value_error(self):
        assert issubclass(MissingClassError, ValueError)


class Versioned(SerializerMixin):
    """Version 2: ``length`` in m. Version 1 had ``length_mm``; version 0 had ``size_mm``."""

    _schema_version = 2

    def __init__(self, length=1.0):
        self.length = length

    @classmethod
    def _migrate(cls, data, version):
        if version < 1:
            data['length_mm'] = data.pop('size_mm')
        if version < 2:
            data['length'] = data.pop('length_mm') / 1000
        return data


def _payload_of(obj_dict):
    return SerializerMixin._MARKER_NONE + msgpack.packb(obj_dict, use_bin_type=True)


class TestSchemaVersion:

    def test_version_zero_is_not_written(self):
        raw = msgpack.unpackb(SimpleSerializable().serialize(compress=False)[1:], raw=False)
        assert '__schema_version__' not in raw

    def test_current_version_is_written_and_loads(self):
        raw = msgpack.unpackb(Versioned(2.0).serialize(compress=False)[1:], raw=False)
        assert raw['__schema_version__'] == 2
        assert Versioned.deserialize(Versioned(2.0).serialize()).length == 2.0

    @pytest.mark.parametrize("version, attributes", [
        (0, {'size_mm': 1500.0}),
        (1, {'length_mm': 1500.0}),
    ])
    def test_older_payload_is_migrated(self, version, attributes):
        payload = {'_class': f"{__name__}.Versioned", **attributes}
        if version:
            payload['__schema_version__'] = version
        restored = Versioned.deserialize(_payload_of(payload))
        assert restored.__dict__ == {'length': 1.5}

    def test_nested_object_is_migrated(self):
        nested = {'__object__': True, '_class': f"{__name__}.Versioned", 'size_mm': 500.0}
        payload = {'_class': f"{__name__}.Holder", 'value': nested}
        assert Holder.deserialize(_payload_of(payload)).value.length == 0.5

    def test_newer_payload_is_rejected(self):
        payload = {'_class': f"{__name__}.Versioned", '__schema_version__': 3, 'length': 1.0}
        with pytest.raises(SchemaVersionError, match="version 3"):
            Versioned.deserialize(_payload_of(payload))
