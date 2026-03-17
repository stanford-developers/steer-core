# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Decorators."""

import pytest

from steer_core.Decorators.General import recalculate, calculate_bulk_properties, calculate_all_properties
from steer_core.Decorators.Coordinates import calculate_coordinates, calculate_areas, calculate_volumes
from steer_core.Decorators.Objects import calculate_weld_tab_properties


class FakeComponent:
    """Minimal component for testing decorators."""

    def __init__(self):
        self._update_properties = True
        self._calls = []

    def _calculate_bulk_properties(self):
        self._calls.append("bulk_properties")

    def _calculate_coordinates(self):
        self._calls.append("coordinates")

    def _calculate_areas(self):
        self._calls.append("areas")

    def _calculate_all_properties(self):
        self._calls.append("all_properties")

    def _calculate_weld_tab_properties(self):
        self._calls.append("weld_tab_properties")


class TestRecalculateDecorator:
    """Tests for the recalculate decorator factory."""

    def test_basic_recalculation(self):
        comp = FakeComponent()

        @recalculate("bulk_properties")
        def set_mass(self, val):
            self._mass = val

        set_mass(comp, 5.0)
        assert comp._mass == 5.0
        assert "bulk_properties" in comp._calls

    def test_multiple_methods(self):
        comp = FakeComponent()

        @recalculate("coordinates", "areas")
        def update(self):
            pass

        update(comp)
        assert comp._calls == ["coordinates", "areas"]

    def test_skipped_when_update_disabled(self):
        comp = FakeComponent()
        comp._update_properties = False

        @recalculate("bulk_properties")
        def set_val(self, v):
            self._val = v

        set_val(comp, 10)
        assert comp._val == 10
        assert comp._calls == []

    def test_requires_guard_passes(self):
        comp = FakeComponent()
        comp._mass = 5.0

        @recalculate("bulk_properties", requires={"_mass": lambda v: v is not None})
        def trigger(self):
            pass

        trigger(comp)
        assert "bulk_properties" in comp._calls

    def test_requires_guard_blocks(self):
        comp = FakeComponent()
        comp._mass = None

        @recalculate("bulk_properties", requires={"_mass": lambda v: v is not None})
        def trigger(self):
            pass

        trigger(comp)
        assert comp._calls == []

    def test_requires_guard_missing_attr(self):
        comp = FakeComponent()
        # No _mass attribute at all

        @recalculate("bulk_properties", requires={"_mass": lambda v: v is not None})
        def trigger(self):
            pass

        trigger(comp)
        assert comp._calls == []

    def test_return_value_preserved(self):
        comp = FakeComponent()

        @recalculate("bulk_properties")
        def compute(self):
            return 42

        assert compute(comp) == 42


class TestPrebuiltDecorators:
    """Tests for pre-built decorator instances."""

    def test_calculate_bulk_properties(self):
        comp = FakeComponent()

        @calculate_bulk_properties
        def do_something(self):
            pass

        do_something(comp)
        assert "bulk_properties" in comp._calls

    def test_calculate_all_properties(self):
        comp = FakeComponent()

        @calculate_all_properties
        def do_something(self):
            pass

        do_something(comp)
        assert "all_properties" in comp._calls

    def test_calculate_coordinates(self):
        comp = FakeComponent()

        @calculate_coordinates
        def do_something(self):
            pass

        do_something(comp)
        assert "coordinates" in comp._calls

    def test_calculate_areas(self):
        comp = FakeComponent()

        @calculate_areas
        def do_something(self):
            pass

        do_something(comp)
        assert "coordinates" in comp._calls
        assert "areas" in comp._calls

    def test_calculate_volumes(self):
        comp = FakeComponent()

        @calculate_volumes
        def do_something(self):
            pass

        do_something(comp)
        assert "bulk_properties" in comp._calls
        assert "coordinates" in comp._calls

    def test_calculate_weld_tab_properties(self):
        comp = FakeComponent()

        @calculate_weld_tab_properties
        def do_something(self):
            pass

        do_something(comp)
        assert "weld_tab_properties" in comp._calls
