# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

from functools import wraps
from typing import Callable, Dict, Optional


def recalculate(*method_names: str, requires: Optional[Dict[str, Callable]] = None):
    """Factory that creates a decorator to call ``self._calculate_<name>()`` after the wrapped method.

    Args:
        *method_names: One or more method suffixes. For each name,
            ``self._calculate_<name>()`` is called in order after the wrapped
            function executes.
        requires: Extra attribute guards. Keys are attribute names
            (e.g. ``"_mass"``), values are callables that receive the attribute
            value and must return ``True`` for the recalculation to proceed.
            All guards must pass.

    Returns:
        A decorator (usable with ``@``) that wraps a method.

    Examples:
        >>> calculate_bulk_properties = recalculate("bulk_properties")
        >>> calculate_areas = recalculate("coordinates", "areas")
        >>> calculate_capacity_curve = recalculate("capacity_curve",
        ...     requires={"_mass": lambda v: v is not None})
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            if hasattr(self, "_update_properties") and self._update_properties:
                if requires:
                    for attr, check in requires.items():
                        if not hasattr(self, attr) or not check(getattr(self, attr)):
                            return result
                for name in method_names:
                    getattr(self, f"_calculate_{name}")()
            return result
        return wrapper
    return decorator


calculate_bulk_properties = recalculate("bulk_properties")
calculate_all_properties = recalculate("all_properties")

