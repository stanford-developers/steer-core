# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Mixin providing standard datum property interface with mm/m unit conversion."""

from typing import Tuple
import numpy as np

from steer_core.Constants.Units import M_TO_MM, MM_TO_M


class DatumMixin:
    """Mixin providing uniform datum coordinate properties.
    
    Expects:
    - `_datum: Tuple[float, float, float]` instance attribute (stored in meters)
    - `validate_datum(value)` method available (from ValidationMixin)
    
    Provides:
    - `datum` property (getter/setter) in millimeters
    - `datum_x`, `datum_y`, `datum_z` properties (getter/setter)
    
    Setter Customization:
    - Override with `@DatumMixin.datum.setter` and add decorators like
      `@calculate_coordinates` or `@calculate_all_properties` as needed
    - For translation-based updates (e.g., assemblies with computed geometry),
      use `_compute_datum_translation()` helper before updating `_datum`

    Examples:
        Recalculation pattern (most common)::
    
        @DatumMixin.datum.setter
        @calculate_coordinates
        def datum(self, value):
            self.validate_datum(value)
            self._datum = tuple(float(v) * MM_TO_M for v in value)
    
    Translation pattern (for complex assemblies):
    
        @DatumMixin.datum.setter
        def datum(self, value):
            self.validate_datum(value)
            translation = self._compute_datum_translation(value)
            if translation:
                self._translate_all_components(translation)
            self._datum = tuple(float(v) * MM_TO_M for v in value)
    """
    
    _datum: Tuple[float, float, float]  # Internal storage in meters
    
    # === MAIN DATUM PROPERTY ===
    
    def _ensure_datum_exists(self) -> None:
        """Ensure _datum attribute exists, initializing to origin if needed."""
        if not hasattr(self, '_datum') or self._datum is None:
            self._datum = (0.0, 0.0, 0.0)
    
    @property
    def datum(self) -> Tuple[float, float, float]:
        """Datum position in millimeters."""
        self._ensure_datum_exists()
        return (
            np.round(self._datum[0] * M_TO_MM, 2),
            np.round(self._datum[1] * M_TO_MM, 2),
            np.round(self._datum[2] * M_TO_MM, 2),
        )
    
    @datum.setter
    def datum(self, value: Tuple[float, float, float]) -> None:
        """Set datum position in millimeters (base implementation).
        
        This base setter only stores the value. Override with decorators
        like @calculate_coordinates to trigger coordinate recalculation,
        or add custom translation logic for complex assemblies.
        """
        self.validate_datum(value)
        self._datum = (
            float(value[0]) * MM_TO_M,
            float(value[1]) * MM_TO_M,
            float(value[2]) * MM_TO_M,
        )
    
    def _compute_datum_translation(self, new_datum_mm: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Compute translation vector from current datum to new datum.

        Args:
            new_datum_mm: New datum position in millimeters.

        Returns:
            Translation vector (dx, dy, dz) in meters, or (0, 0, 0) if no existing datum.
        """
        if not hasattr(self, '_datum') or self._datum is None:
            return (0.0, 0.0, 0.0)
        
        return (
            float(new_datum_mm[0]) * MM_TO_M - self._datum[0],
            float(new_datum_mm[1]) * MM_TO_M - self._datum[1],
            float(new_datum_mm[2]) * MM_TO_M - self._datum[2],
        )
    
    # === INDIVIDUAL COORDINATE PROPERTIES ===
    
    @property
    def datum_x(self) -> float:
        """X-coordinate of datum in millimeters."""
        self._ensure_datum_exists()
        return np.round(self._datum[0] * M_TO_MM, 2)
    
    @datum_x.setter
    def datum_x(self, x: float) -> None:
        """Set X-coordinate of datum in millimeters."""
        self.datum = (x, self.datum[1], self.datum[2])
    
    @property
    def datum_y(self) -> float:
        """Y-coordinate of datum in millimeters."""
        self._ensure_datum_exists()
        return np.round(self._datum[1] * M_TO_MM, 2)
    
    @datum_y.setter
    def datum_y(self, y: float) -> None:
        """Set Y-coordinate of datum in millimeters."""
        self.datum = (self.datum[0], y, self.datum[2])
    
    @property
    def datum_z(self) -> float:
        """Z-coordinate of datum in millimeters."""
        self._ensure_datum_exists()
        return np.round(self._datum[2] * M_TO_MM, 2)
    
    @datum_z.setter
    def datum_z(self, z: float) -> None:
        """Set Z-coordinate of datum in millimeters."""
        self.datum = (self.datum[0], self.datum[1], z)
    
