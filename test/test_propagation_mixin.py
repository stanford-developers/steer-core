# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for steer_core.Mixins.Propagation."""

import pytest

from steer_core.Mixins.Propagation import PropagationMixin, propagating_setter


class Child(PropagationMixin):
    def __init__(self, name="child"):
        self._name = name
        self._update_properties = True
        self._parent = None
        self._parent_attr_name = None

    @property
    def name(self):
        return self._name

    def _calculate_all_properties(self):
        self._recalculated = True


class Parent(PropagationMixin):
    def __init__(self):
        self._child = None
        self._update_properties = True
        self._parent = None
        self._parent_attr_name = None
        self._set_child_called = False

    @property
    def child(self):
        return self._child

    @child.setter
    def child(self, value):
        old = self._child
        if old is not None and old is not value and hasattr(old, "_set_parent"):
            old._set_parent(None)
        self._child = value
        if value is not None and hasattr(value, "_set_parent"):
            value._set_parent(self, "child")
        self._set_child_called = True

    def _calculate_all_properties(self):
        pass


class TestParentChildReferences:

    def test_set_parent(self):
        child = Child()
        parent = Parent()
        child._set_parent(parent, "child")
        assert child._get_parent() is parent
        assert child._parent_attr_name == "child"

    def test_clear_parent(self):
        child = Child()
        parent = Parent()
        child._set_parent(parent, "child")
        child._set_parent(None)
        assert child._get_parent() is None
        assert child._parent_attr_name is None


class TestUpdate:

    def test_update_triggers_parent_setter(self):
        parent = Parent()
        child = Child()
        parent.child = child
        parent._set_child_called = False
        child.update()
        assert parent._set_child_called is True

    def test_update_no_parent_calls_calculate(self):
        child = Child()
        child.update()
        assert getattr(child, "_recalculated", False) is True


class TestPropagateChanges:

    def test_propagate_up_one_level(self):
        parent = Parent()
        child = Child()
        parent.child = child
        parent._set_child_called = False
        child.propagate_changes()
        assert parent._set_child_called is True


class TestBatchUpdates:

    def test_batch_suppresses_recalculation(self):
        child = Child()
        child._recalculated = False

        with child.batch_updates():
            assert child._update_properties is False

        # _calculate_all_properties should have been called on exit
        assert child._recalculated is True

    def test_batch_restores_flag(self):
        child = Child()
        original = child._update_properties
        with child.batch_updates():
            pass
        assert child._update_properties == original


class TestPropagatingSetter:

    def test_basic_propagating_setter(self):
        class TestParent(PropagationMixin):
            def __init__(self):
                self._item = None
                self._parent = None
                self._parent_attr_name = None

            @property
            def item(self):
                return self._item

            @item.setter
            @propagating_setter()
            def item(self, value):
                self._item = value

        parent = TestParent()
        child = Child()
        parent.item = child
        assert child._get_parent() is parent
        assert child._parent_attr_name == "item"

    def test_propagating_setter_clears_old_parent(self):
        class TestParent(PropagationMixin):
            def __init__(self):
                self._item = None
                self._parent = None
                self._parent_attr_name = None

            @property
            def item(self):
                return self._item

            @item.setter
            @propagating_setter()
            def item(self, value):
                self._item = value

        parent = TestParent()
        old_child = Child("old")
        new_child = Child("new")

        parent.item = old_child
        parent.item = new_child

        assert old_child._get_parent() is None
        assert new_child._get_parent() is parent
