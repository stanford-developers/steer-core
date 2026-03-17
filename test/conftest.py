# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shared fixtures for steer-core tests."""

import numpy as np
import pytest

from steer_core.Mixins.TypeChecker import ValidationMixin
from steer_core.Mixins.Datum import DatumMixin
from steer_core.Mixins.Dunder import DunderMixin
from steer_core.Mixins.Serializer import SerializerMixin
from steer_core.Mixins.Propagation import PropagationMixin


class SampleObject(
    ValidationMixin,
    DatumMixin,
    DunderMixin,
    SerializerMixin,
    PropagationMixin,
):
    """Minimal concrete class composing multiple mixins for testing."""

    def __init__(self, name: str = "test", value: float = 1.0):
        self._name = name
        self._value = value
        self._datum = (0.0, 0.0, 0.0)
        self._update_properties = True
        self._parent = None
        self._parent_attr_name = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, v: float):
        self._value = v

    def _calculate_all_properties(self):
        """Stub for recalculation hooks."""
        pass


@pytest.fixture
def sample_obj():
    """Return a fresh SampleObject."""
    return SampleObject()


@pytest.fixture
def sample_coords_2d():
    """Simple 2D coordinate array."""
    return np.array([
        [0.0, 0.0],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0],
    ])


@pytest.fixture
def sample_coords_3d():
    """Simple 3D coordinate array (unit square in XY plane)."""
    return np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
    ])
