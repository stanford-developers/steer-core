

import typing

import numpy as np

from steer_core.Utils import is_plotly_trace

# Numeric types accepted by the float-property class-level introspection.
_NUMERIC_TYPES = (float, int, np.floating, np.integer)


class DunderMixin:

    # ── instance methods (unchanged API) ───────────────────────────────

    def _get_comparable_float_properties(self):
        """Get all @property decorated attributes that return floats."""
        float_properties = []
        for cls in self.__class__.__mro__:
            for name, value in cls.__dict__.items():
                if isinstance(value, property):
                    if not self._should_exclude_property_viewable_stat(name):
                        try:
                            prop_value = getattr(self, name)
                            if isinstance(prop_value, (float, np.floating, int, np.integer)):
                                float_properties.append(name)
                        except (AttributeError, TypeError):
                            continue  # Skip properties that raise exceptions
        return float_properties

    def _get_comparable_properties(self):
        """Get all comparable properties from the class hierarchy."""
        properties = []
        for cls in self.__class__.__mro__:
            for name, value in cls.__dict__.items():
                if isinstance(value, property):
                    if not self._should_exclude_property(name):
                        properties.append(name)
        return properties

    def _should_exclude_property(self, name):
        """Check if a property should be excluded from comparison."""
        return DunderMixin._should_exclude_property_static(name)

    def _should_exclude_property_viewable_stat(self, name):
        """Check if a property should be excluded from viewable stats."""
        return DunderMixin._should_exclude_property_viewable_stat_static(name)

    # ── static helpers (no instance required) ──────────────────────────

    @staticmethod
    def _should_exclude_property_static(name: str) -> bool:
        """Check if a property should be excluded from comparison."""
        return (
            name.endswith('_trace') or
            name.endswith('_range') or
            name in {'last_updated', 'properties'}
        )

    @staticmethod
    def _should_exclude_property_viewable_stat_static(name: str) -> bool:
        """Check if a property should be excluded from viewable stats."""
        return (
            name.endswith('_trace') or
            name.endswith('_range') or
            name in {'last_updated', 'properties'} or
            'datum' in name.lower()
        )

    @staticmethod
    def _is_numeric_annotation(annotation) -> bool:
        """Return True if *annotation* resolves to a numeric type.

        Handles plain types (``float``, ``int``), numpy scalar types,
        ``Optional[float]``,  ``Union[float, int]``, etc.
        """
        if annotation is typing.Any:
            return False
        origin = getattr(annotation, '__origin__', None)
        if origin is typing.Union:
            # e.g. Optional[float] == Union[float, None]
            return any(
                DunderMixin._is_numeric_annotation(arg)
                for arg in annotation.__args__
                if arg is not type(None)
            )
        try:
            if isinstance(annotation, type) and issubclass(annotation, _NUMERIC_TYPES):
                return True
        except TypeError:
            pass
        return False

    @classmethod
    def _get_comparable_float_properties_from_class(cls) -> list[str]:
        """Discover float-valued ``@property`` names by inspecting the class hierarchy.

        Unlike the instance method ``_get_comparable_float_properties`` this
        does **not** require a live object.  It walks the MRO, finds
        ``property`` descriptors, applies the viewable-stat exclusion filter,
        and then checks the ``fget`` return annotation.  If a property has a
        numeric return annotation it is included; if it has *no* annotation
        at all it is included as well (permissive fallback).  Properties
        that are explicitly annotated as a non-numeric type are excluded.
        """
        seen: set[str] = set()
        float_properties: list[str] = []
        for klass in cls.__mro__:
            for name, value in klass.__dict__.items():
                if name in seen:
                    continue
                seen.add(name)
                if not isinstance(value, property):
                    continue
                if DunderMixin._should_exclude_property_viewable_stat_static(name):
                    continue

                # --- check return annotation of property.fget ---
                fget = value.fget
                if fget is None:
                    continue
                try:
                    hints = typing.get_type_hints(fget)
                except (AttributeError, TypeError, NameError):
                    hints = {}
                ret = hints.get('return')
                if ret is None:
                    # No annotation → include (permissive fallback).
                    float_properties.append(name)
                elif DunderMixin._is_numeric_annotation(ret):
                    float_properties.append(name)
                # else: explicitly non-numeric → skip
        return float_properties

    @staticmethod
    def _is_plotly_trace(obj):
        """Check if object is a Plotly trace object."""
        return is_plotly_trace(obj)

    def _compare_none_values(self, self_value, other_value):
        """Compare None values. Returns (should_continue, result)."""
        if self_value is None and other_value is None:
            return True, True  # Continue, values are equal
        elif self_value is None or other_value is None:
            return False, False  # Stop, values are not equal
        return True, None  # Continue, not None values

    def _compare_plotly_traces(self, self_value, other_value):
        """Compare Plotly trace objects. Returns (should_continue, result)."""
        if self._is_plotly_trace(self_value) or self._is_plotly_trace(other_value):
            return True, True  # Skip Plotly traces, continue
        return True, None  # Continue, not Plotly traces

    def _compare_numpy_arrays(self, self_value, other_value):
        """Compare NumPy arrays. Returns (should_continue, result)."""
        if isinstance(self_value, np.ndarray) and isinstance(other_value, np.ndarray):
            return False, np.array_equal(self_value, other_value, equal_nan=True)
        elif isinstance(self_value, np.ndarray) or isinstance(other_value, np.ndarray):
            return False, False  # One is numpy array, other is not
        return True, None  # Continue, not numpy arrays

    def _compare_dataframes(self, self_value, other_value):
        """Compare pandas DataFrames/Series. Returns (should_continue, result)."""
        if hasattr(self_value, 'equals') and hasattr(other_value, 'equals'):
            return False, self_value.equals(other_value)
        elif hasattr(self_value, 'equals') or hasattr(other_value, 'equals'):
            return False, False  # Only one is a DataFrame/Series
        return True, None  # Continue, not DataFrames

    def _compare_dictionaries(self, self_value, other_value):
        """Compare dictionaries by comparing keys and values separately. Returns (should_continue, result)."""
        if isinstance(self_value, dict) and isinstance(other_value, dict):
            if len(self_value) != len(other_value):
                return False, False

            # Compare ordered key-value pairs using __eq__ (not hash-based)
            # so that objects with identity-based __hash__ still compare
            # correctly when they are value-equal.
            for (k1, v1), (k2, v2) in zip(self_value.items(), other_value.items()):
                if k1 != k2 or v1 != v2:
                    return False, False

            return False, True
        elif isinstance(self_value, dict) or isinstance(other_value, dict):
            return False, False  # One is dict, other is not
        return True, None  # Continue, not dictionaries

    def _compare_sequences(self, self_value, other_value):
        """Compare lists and tuples. Returns (should_continue, result)."""
        if isinstance(self_value, (list, tuple)) and isinstance(other_value, (list, tuple)):
            return False, type(self_value) == type(other_value) and self_value == other_value
        elif isinstance(self_value, (list, tuple)) or isinstance(other_value, (list, tuple)):
            return False, False  # One is sequence, other is not
        return True, None  # Continue, not sequences

    def _compare_other_types(self, self_value, other_value):
        """Compare all other types. Returns (should_continue, result)."""
        return False, self_value == other_value

    def __eq__(self, other):
        """
        Compare two instances based on all their @property decorated attributes.
        
        Returns True if all properties have equal values, False otherwise.
        Returns False if other is not an instance of the same class.
        """
        # Quick identity check first (performance optimization)
        if self is other:
            return True
            
        # Check if other is the same type
        if type(other) != type(self):
            return False
        
        # Cache properties to avoid repeated computation (performance optimization)
        if not hasattr(self, '_cached_properties'):
            self._cached_properties = self._get_comparable_properties()
        
        # Define comparison methods in order of priority/frequency
        comparison_methods = [
            self._compare_none_values,
            self._compare_plotly_traces,
            self._compare_numpy_arrays,
            self._compare_dataframes,
            self._compare_dictionaries,
            self._compare_sequences,
            self._compare_other_types,
        ]

        # Compare all property values
        for prop_name in self._cached_properties:

            try:
                self_value = getattr(self, prop_name)
                other_value = getattr(other, prop_name)
                
                # Execute comparison methods until one handles the values
                for method in comparison_methods:
                    should_continue, result = method(self_value, other_value)
                    if not should_continue:
                        if not result:
                            return False
                        break  # Values are equal, continue to next property
                        
            except (AttributeError, TypeError):
                return False
        
        return True
    
    def __hash__(self):
        """Hash based on object identity.

        Because the objects using this mixin are mutable, a content-based
        hash would be unstable.  Using ``id()`` means that two distinct
        objects that compare equal via ``__eq__`` will have different
        hashes -- avoid using these objects as ``set`` members or ``dict``
        keys when value-based identity matters.
        """
        return hash(id(self))
    
    def __str__(self):
        """
        String representation of the instance showing all @property decorated attributes and their values.
        """
        if hasattr(self, 'name') and self.name:
            return f"{self.__class__.__name__} ({self.name})"
        else:
            return f"{self.__class__.__name__}"
    
    def __repr__(self):
        """
        Official string representation of the instance.
        """
        return self.__str__()

