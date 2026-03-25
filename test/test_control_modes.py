# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Utils.ControlModes."""

from enum import Enum

import pytest

from steer_core.Utils.ControlModes import dispatch_dependent_update


class Mode(Enum):
    HOLD_A = "hold_a"
    HOLD_B = "hold_b"
    HOLD_C = "hold_c"


def add(x, y):
    return x + y

def multiply(x, y):
    return x * y

def subtract(x, y):
    return x - y


class TestDispatchDependentUpdate:

    def test_basic_dispatch(self):
        dep_map = {
            Mode.HOLD_A: {"b": add, "c": multiply},
            Mode.HOLD_B: {"a": subtract, "c": add},
        }
        input_map = {
            Mode.HOLD_A: {"b": (3, 4), "c": (5, 6)},
            Mode.HOLD_B: {"a": (10, 3), "c": (1, 2)},
        }

        assert dispatch_dependent_update(Mode.HOLD_A, "b", dep_map, input_map) == 7
        assert dispatch_dependent_update(Mode.HOLD_A, "c", dep_map, input_map) == 30
        assert dispatch_dependent_update(Mode.HOLD_B, "a", dep_map, input_map) == 7
        assert dispatch_dependent_update(Mode.HOLD_B, "c", dep_map, input_map) == 3

    def test_unknown_mode_raises(self):
        dep_map = {Mode.HOLD_A: {"x": add}}
        input_map = {Mode.HOLD_A: {"x": (1, 2)}}

        with pytest.raises(KeyError):
            dispatch_dependent_update(Mode.HOLD_C, "x", dep_map, input_map)

    def test_unknown_property_raises(self):
        dep_map = {Mode.HOLD_A: {"x": add}}
        input_map = {Mode.HOLD_A: {"x": (1, 2)}}

        with pytest.raises(KeyError):
            dispatch_dependent_update(Mode.HOLD_A, "y", dep_map, input_map)

    def test_single_arg_dispatch(self):
        def negate(x):
            return -x

        dep_map = {Mode.HOLD_A: {"x": negate}}
        input_map = {Mode.HOLD_A: {"x": (42,)}}

        assert dispatch_dependent_update(Mode.HOLD_A, "x", dep_map, input_map) == -42

    def test_side_effects(self):
        results = []

        def record(val):
            results.append(val)

        dep_map = {Mode.HOLD_A: {"x": record}}
        input_map = {Mode.HOLD_A: {"x": ("hello",)}}

        dispatch_dependent_update(Mode.HOLD_A, "x", dep_map, input_map)
        assert results == ["hello"]

    def test_three_mode_three_property(self):
        """Mimics the electrode control pattern with 3 modes and 3 properties."""
        dep_map = {
            Mode.HOLD_A: {"a": add,      "b": multiply, "c": subtract},
            Mode.HOLD_B: {"a": multiply, "b": add,      "c": subtract},
            Mode.HOLD_C: {"a": subtract, "b": subtract, "c": add},
        }
        input_map = {
            Mode.HOLD_A: {"a": (1, 2), "b": (3, 4), "c": (10, 3)},
            Mode.HOLD_B: {"a": (2, 3), "b": (5, 5), "c": (8, 2)},
            Mode.HOLD_C: {"a": (9, 4), "b": (7, 1), "c": (2, 2)},
        }

        # HOLD_A: a→add(1,2)=3, b→multiply(3,4)=12, c→subtract(10,3)=7
        assert dispatch_dependent_update(Mode.HOLD_A, "a", dep_map, input_map) == 3
        assert dispatch_dependent_update(Mode.HOLD_A, "b", dep_map, input_map) == 12
        assert dispatch_dependent_update(Mode.HOLD_A, "c", dep_map, input_map) == 7

        # HOLD_B: a→multiply(2,3)=6
        assert dispatch_dependent_update(Mode.HOLD_B, "a", dep_map, input_map) == 6

        # HOLD_C: c→add(2,2)=4
        assert dispatch_dependent_update(Mode.HOLD_C, "c", dep_map, input_map) == 4
