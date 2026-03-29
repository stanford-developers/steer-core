# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Generic utilities for processing paired directional curves.

Operates on numpy arrays with columns ``[x, y, direction]`` where
``direction`` is ``1`` (primary segment) or ``-1`` (secondary segment).
"""

import numpy as np
from typing import List

from steer_core.Mixins.Data import DataMixin


def correct_segment_directions(curve: np.ndarray) -> np.ndarray:
    """Ensure the primary segment (direction=1) has the larger x-range.

    If the secondary segment has a larger x excursion, the direction
    labels are swapped.

    Parameters
    ----------
    curve : np.ndarray
        Array of shape (n, 3) with columns ``[x, y, direction]``.

    Returns
    -------
    np.ndarray
        Curve with corrected direction labels.
    """
    primary = curve[curve[:, 2] == 1]
    secondary = curve[curve[:, 2] == -1]

    if len(primary) == 0 or len(secondary) == 0:
        return curve

    primary_range = primary[:, 0].max() - primary[:, 0].min()
    secondary_range = secondary[:, 0].max() - secondary[:, 0].min()

    if primary_range > secondary_range:
        return curve
    else:
        primary[:, 2] = -1
        secondary[:, 2] = 1
        return np.concatenate([secondary, primary], axis=0)


def make_segments_monotonic(curve: np.ndarray) -> np.ndarray:
    """Force both segments to be monotonic in their x and y columns.

    Uses PCHIP interpolation via ``DataMixin.enforce_monotonicity()``.

    Parameters
    ----------
    curve : np.ndarray
        Array with columns ``[x, y, direction]``.

    Returns
    -------
    np.ndarray
        Curve with monotonic x and y within each segment.
    """
    primary = curve[curve[:, 2] == 1].copy()
    secondary = curve[curve[:, 2] == -1].copy()

    primary[:, 0] = DataMixin.enforce_monotonicity(primary[:, 0])
    primary[:, 1] = DataMixin.enforce_monotonicity(primary[:, 1])

    secondary[:, 0] = DataMixin.enforce_monotonicity(secondary[:, 0])
    secondary[:, 1] = DataMixin.enforce_monotonicity(secondary[:, 1])

    return np.concatenate([primary, secondary], axis=0)


def reverse_secondary_segment(curve: np.ndarray) -> np.ndarray:
    """Mirror the secondary segment so its x-values decrease from the curve maximum.

    Parameters
    ----------
    curve : np.ndarray
        Array with columns ``[x, y, direction]``.

    Returns
    -------
    np.ndarray
        Curve with the secondary segment's x-values reflected about the
        maximum x of the entire curve.
    """
    max_x = curve[:, 0].max()
    primary = curve[curve[:, 2] == 1].copy()
    secondary = curve[curve[:, 2] == -1].copy()
    secondary[:, 0] = -secondary[:, 0] + max_x
    return np.concatenate([primary, secondary], axis=0)


def prepend_primary_endpoint_to_secondary(curve: np.ndarray) -> np.ndarray:
    """Prepend the last primary-segment point to the secondary segment.

    Ensures both segments share a common junction point.

    Parameters
    ----------
    curve : np.ndarray
        Array with columns ``[x, y, direction]``.

    Returns
    -------
    np.ndarray
        Curve with junction point added to the secondary segment.
    """
    primary = curve[curve[:, 2] == 1].copy()
    secondary = curve[curve[:, 2] == -1].copy()
    junction = primary[-1, :].copy()
    junction[2] = -1
    secondary = np.vstack([junction, secondary])
    return np.concatenate([primary, secondary], axis=0)


def scale_secondary_segment(curve: np.ndarray, scaling: float) -> np.ndarray:
    """Scale the secondary segment's x-values relative to the curve maximum.

    Parameters
    ----------
    curve : np.ndarray
        Array with columns ``[x, y, direction]``.
    scaling : float
        Scaling factor applied to the secondary segment.

    Returns
    -------
    np.ndarray
        Curve with scaled secondary segment.
    """
    curve_copy = curve.copy()
    primary = curve_copy[curve_copy[:, 2] == 1].copy()
    secondary = curve_copy[curve_copy[:, 2] == -1].copy()
    max_x = curve_copy[:, 0].max()

    secondary[:, 0] = (
        scaling * (secondary[:, 0] - max_x) + max_x
    )

    return np.concatenate([primary, secondary], axis=0)


def scale_curve(curve: np.ndarray, scaling: float) -> np.ndarray:
    """Uniformly scale all x-values in the curve.

    Parameters
    ----------
    curve : np.ndarray
        Array with columns ``[x, y, direction]``.
    scaling : float
        Factor applied to x-values.

    Returns
    -------
    np.ndarray
        Curve with globally scaled x-axis.
    """
    result = curve.copy()
    result[:, 0] = result[:, 0] * scaling
    return result


def interpolate_between_curves(
    target_value: float,
    below_curve: np.ndarray,
    above_curve: np.ndarray,
    below_y_max: float,
    above_y_max: float,
    n_points: int = 100,
) -> np.ndarray:
    """Interpolate between two single-segment curves at a target maximum y-value.

    Handles both primary (ascending x) and secondary (descending x) segments.

    Parameters
    ----------
    target_value : float
        Target y-value to interpolate at.
    below_curve : np.ndarray
        Curve whose y-max is below the target.
    above_curve : np.ndarray
        Curve whose y-max is above the target.
    below_y_max : float
        Maximum y of the below curve.
    above_y_max : float
        Maximum y of the above curve.
    n_points : int
        Number of interpolation points.

    Returns
    -------
    np.ndarray
        Interpolated curve with shape ``(n_points, 3)``.
    """
    if np.isclose(below_y_max, above_y_max):
        return below_curve.copy()

    is_secondary = (
        below_curve[0, 2] == -1 if len(below_curve) > 0 else above_curve[0, 2] == -1
    )

    if is_secondary:
        below_sorted = below_curve[np.argsort(below_curve[:, 0])[::-1]]
        above_sorted = above_curve[np.argsort(above_curve[:, 0])[::-1]]

        x_grid_low = np.linspace(
            below_sorted[:, 0].min(), below_sorted[:, 0].max(), n_points
        )
        x_grid_high = np.linspace(
            above_sorted[:, 0].min(), above_sorted[:, 0].max(), n_points
        )

        y_low_interp = np.interp(
            x_grid_low, below_sorted[:, 0][::-1], below_sorted[:, 1][::-1]
        )
        y_high_interp = np.interp(
            x_grid_high, above_sorted[:, 0][::-1], above_sorted[:, 1][::-1]
        )
    else:
        below_sorted = below_curve[np.argsort(below_curve[:, 0])]
        above_sorted = above_curve[np.argsort(above_curve[:, 0])]

        x_grid_low = np.linspace(
            below_sorted[:, 0].min(), below_sorted[:, 0].max(), n_points
        )
        x_grid_high = np.linspace(
            above_sorted[:, 0].min(), above_sorted[:, 0].max(), n_points
        )

        y_low_interp = np.interp(
            x_grid_low, below_sorted[:, 0], below_sorted[:, 1]
        )
        y_high_interp = np.interp(
            x_grid_high, above_sorted[:, 0], above_sorted[:, 1]
        )

    weight_low = (above_y_max - target_value) / (above_y_max - below_y_max)
    weight_high = (target_value - below_y_max) / (above_y_max - below_y_max)

    x_values = x_grid_low * weight_low + x_grid_high * weight_high
    y_interp = y_low_interp * weight_low + y_high_interp * weight_high

    direction = below_curve[0, 2] if len(below_curve) > 0 else above_curve[0, 2]

    interpolated = np.column_stack(
        [x_values, y_interp, np.full(n_points, direction)]
    )

    if is_secondary:
        interpolated = interpolated[np.argsort(interpolated[:, 0])[::-1]]

    return interpolated


def interpolate_curve_at_target(
    curves: List[np.ndarray],
    target_y: float,
    n_points: int = 100,
) -> np.ndarray:
    """Find bounding curves and interpolate to match a target y-value at max x.

    Parameters
    ----------
    curves : list[np.ndarray]
        Collection of curves with columns ``[x, y, direction]``.
    target_y : float
        Target y-value at maximum x to interpolate between.
    n_points : int
        Number of interpolation points per segment.

    Returns
    -------
    np.ndarray
        Interpolated curve.
    """
    y_at_max_x = []
    for curve in curves:
        max_x_idx = np.argmax(curve[:, 0])
        y_at_max_x.append(curve[max_x_idx, 1])
    y_at_max_x = np.array(y_at_max_x)

    below_mask = y_at_max_x <= target_y
    max_below = np.max(y_at_max_x[below_mask])
    below_idx = np.where(y_at_max_x == max_below)[0][0]
    below_curve = curves[below_idx]

    above_mask = y_at_max_x >= target_y
    min_above = np.min(y_at_max_x[above_mask])
    above_idx = np.where(y_at_max_x == min_above)[0][0]
    above_curve = curves[above_idx]

    below_primary = below_curve[below_curve[:, 2] == 1]
    below_secondary = below_curve[below_curve[:, 2] == -1]
    above_primary = above_curve[above_curve[:, 2] == 1]
    above_secondary = above_curve[above_curve[:, 2] == -1]

    primary_interp = interpolate_between_curves(
        target_y, below_primary, above_primary, max_below, min_above, n_points
    )
    secondary_interp = interpolate_between_curves(
        target_y, below_secondary, above_secondary, max_below, min_above, n_points
    )

    secondary_interp = secondary_interp[np.argsort(secondary_interp[:, 0])[::-1]]

    return np.vstack([primary_interp, secondary_interp])


def prepare_arrays_for_interp(
    x_array: np.ndarray, y_array: np.ndarray
) -> tuple:
    """Ensure arrays are monotonically increasing for ``np.interp``.

    If both arrays are decreasing, flip both. If only x is decreasing,
    sort by x ascending.

    Parameters
    ----------
    x_array : np.ndarray
        The x values.
    y_array : np.ndarray
        The y values.

    Returns
    -------
    tuple
        ``(x_sorted, y_sorted)`` both monotonically increasing.
    """
    x_increasing = np.all(np.diff(x_array) >= 0) or np.mean(np.diff(x_array)) > 0
    y_increasing = np.all(np.diff(y_array) >= 0) or np.mean(np.diff(y_array)) > 0

    if not x_increasing and not y_increasing:
        return x_array[::-1], y_array[::-1]
    elif not x_increasing:
        sort_idx = np.argsort(x_array)
        return x_array[sort_idx], y_array[sort_idx]
    else:
        return x_array, y_array


def truncate_and_shift_segments(
    curves: List[np.ndarray],
    y_cutoff: float,
    truncate_below_cutoff: bool = True,
) -> np.ndarray:
    """Truncate curve segments at a y-cutoff and align x-axes.

    Parameters
    ----------
    curves : list[np.ndarray]
        Collection of curves with columns ``[x, y, direction]``.
    y_cutoff : float
        y-value at which to truncate.
    truncate_below_cutoff : bool
        If ``True``, keep points where ``y <= y_cutoff`` (cutoff is
        an upper bound). If ``False``, keep points where ``y >= y_cutoff``
        (cutoff is a lower bound).

    Returns
    -------
    np.ndarray
        Combined curve truncated at the cutoff with the secondary segment
        shifted to share the same x origin as the primary segment.
    """
    y_at_max_x = [curve[np.argmax(curve[:, 0]), 1] for curve in curves]
    min_y_curve = curves[np.argmin(y_at_max_x)].copy()

    primary = min_y_curve[min_y_curve[:, 2] == 1]
    secondary = min_y_curve[min_y_curve[:, 2] == -1]

    primary_y_sorted, primary_x_sorted = prepare_arrays_for_interp(
        primary[:, 1], primary[:, 0]
    )
    secondary_y_sorted, secondary_x_sorted = prepare_arrays_for_interp(
        secondary[:, 1], secondary[:, 0]
    )

    primary_x_interp = np.interp(y_cutoff, primary_y_sorted, primary_x_sorted)
    secondary_x_interp = np.interp(y_cutoff, secondary_y_sorted, secondary_x_sorted)

    primary_ext = np.vstack([primary, [primary_x_interp, y_cutoff, 1]])
    secondary_ext = np.vstack([[secondary_x_interp, y_cutoff, -1], secondary])

    if truncate_below_cutoff:
        y_condition = lambda v: v <= y_cutoff
    else:
        y_condition = lambda v: v >= y_cutoff

    primary_final = primary_ext[y_condition(primary_ext[:, 1])]
    secondary_final = secondary_ext[y_condition(secondary_ext[:, 1])]

    primary_at_cutoff = primary_final[
        np.isclose(primary_final[:, 1], y_cutoff), 0
    ][0]
    secondary_at_cutoff = secondary_final[
        np.isclose(secondary_final[:, 1], y_cutoff), 0
    ][0]

    secondary_final[:, 0] += primary_at_cutoff - secondary_at_cutoff

    return np.vstack([primary_final, secondary_final])
