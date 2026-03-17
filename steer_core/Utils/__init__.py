# SPDX-License-Identifier: AGPL-3.0-only

"""Utility functions for the steer-core package."""

from typing import Any

import numpy as np


def is_plotly_trace(obj: object) -> bool:
    """Return ``True`` if *obj* is a Plotly trace object."""
    return (
        hasattr(obj, '__module__')
        and obj.__module__
        and obj.__module__.startswith('plotly.graph_objs')
    )


def round_dict_recursive(
    obj: Any, precision: int = 2, unit_conversion: float = 1.0
) -> Any:
    """Recursively round values in a nested dictionary.

    Parameters
    ----------
    obj : Any
        Dictionary or numeric value to round.
    precision : int, optional
        Number of decimal places, by default 2.
    unit_conversion : float, optional
        Multiplicative factor applied before rounding, by default 1.0.

    Returns
    -------
    Any
        Rounded dictionary or value.
    """
    if isinstance(obj, dict):
        return {
            k: round_dict_recursive(v, precision, unit_conversion)
            for k, v in obj.items()
        }
    return np.round(obj * unit_conversion, precision)
