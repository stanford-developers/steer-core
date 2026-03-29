# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Utility functions for the steer-core package."""

from typing import Any

import numpy as np

from steer_core.Utils.CurveProcessing import (  # noqa: F401
    correct_segment_directions,
    make_segments_monotonic,
    reverse_secondary_segment,
    prepend_primary_endpoint_to_secondary,
    scale_secondary_segment,
    scale_curve,
    interpolate_between_curves,
    interpolate_curve_at_target,
    prepare_arrays_for_interp,
    truncate_and_shift_segments,
)
from steer_core.Utils.CurveComposition import (  # noqa: F401
    build_zero_value_proxy,
    compute_paired_curve_difference,
    DEFAULT_INTERPOLATION_POINTS,
)
from steer_core.Utils.ControlModes import (  # noqa: F401
    dispatch_dependent_update,
)


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

    Args:
        obj: Dictionary or numeric value to round.
        precision: Number of decimal places, by default 2.
        unit_conversion: Multiplicative factor applied before rounding, by default 1.0.

    Returns:
        Rounded dictionary or value.
    """
    if isinstance(obj, dict):
        return {
            k: round_dict_recursive(v, precision, unit_conversion)
            for k, v in obj.items()
        }
    return np.round(obj * unit_conversion, precision)
