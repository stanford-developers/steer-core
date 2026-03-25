# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Generic utilities for composing paired directional curves.

Combines two curve sources via interpolation on a common x-axis and
computes their difference.
"""

import numpy as np
from typing import Tuple


DEFAULT_INTERPOLATION_POINTS = 100


def build_zero_value_proxy(
    reference_curve: np.ndarray,
    n_points: int = DEFAULT_INTERPOLATION_POINTS,
) -> np.ndarray:
    """Build a synthetic zero-y curve spanning the reference curve's x-range.

    Useful as a proxy when one of two paired curves is absent.

    Parameters
    ----------
    reference_curve : np.ndarray
        Reference curve with columns ``[x, y, direction]``.
    n_points : int
        Number of points per segment.

    Returns
    -------
    np.ndarray
        Synthetic curve with shape ``(2*n_points, 3)`` where y is ``0.0``.
    """
    primary_mask = reference_curve[:, 2] == 1
    secondary_mask = reference_curve[:, 2] == -1

    primary_x_min = reference_curve[primary_mask, 0].min()
    primary_x_max = reference_curve[primary_mask, 0].max()
    secondary_x_min = reference_curve[secondary_mask, 0].min()
    secondary_x_max = reference_curve[secondary_mask, 0].max()

    proxy = np.empty((2 * n_points, 3))

    proxy[:n_points, 0] = np.linspace(primary_x_min, primary_x_max, n_points)
    proxy[:n_points, 1] = 0.0
    proxy[:n_points, 2] = 1

    proxy[n_points:, 0] = np.linspace(secondary_x_max, secondary_x_min, n_points)
    proxy[n_points:, 1] = 0.0
    proxy[n_points:, 2] = -1

    return proxy


def compute_paired_curve_difference(
    curve_a: np.ndarray,
    curve_b: np.ndarray,
    n_points: int = DEFAULT_INTERPOLATION_POINTS,
) -> Tuple[float, np.ndarray]:
    """Combine two curves by computing ``y_a - y_b`` on their common x-range.

    Both curves must have columns ``[x, y, direction]`` where direction is
    ``1`` (primary) or ``-1`` (secondary).

    Parameters
    ----------
    curve_a : np.ndarray
        First curve (positive contribution to the difference).
    curve_b : np.ndarray
        Second curve (subtracted from curve_a).
    n_points : int
        Number of interpolation points per segment.

    Returns
    -------
    Tuple[float, np.ndarray]
        - ratio: ``max_x_b / max_x_a``
        - combined curve with shape ``(2*n_points, 3)``
    """
    max_x_a = curve_a[:, 0].max()
    max_x_b = curve_b[:, 0].max()
    ratio = max_x_b / max_x_a

    a_primary_mask = curve_a[:, 2] == 1
    a_secondary_mask = curve_a[:, 2] == -1
    b_primary_mask = curve_b[:, 2] == 1
    b_secondary_mask = curve_b[:, 2] == -1

    a_primary = curve_a[a_primary_mask]
    a_secondary = curve_a[a_secondary_mask]
    b_primary = curve_b[b_primary_mask]
    b_secondary = curve_b[b_secondary_mask]

    primary_x_min = max(a_primary[:, 0].min(), b_primary[:, 0].min())
    primary_x_max = min(a_primary[:, 0].max(), b_primary[:, 0].max())
    secondary_x_min = max(a_secondary[:, 0].min(), b_secondary[:, 0].min())
    secondary_x_max = min(a_secondary[:, 0].max(), b_secondary[:, 0].max())

    a_primary_idx = a_primary[:, 0].argsort()
    a_secondary_idx = a_secondary[:, 0].argsort()
    b_primary_idx = b_primary[:, 0].argsort()
    b_secondary_idx = b_secondary[:, 0].argsort()

    primary_x_common = np.linspace(primary_x_min, primary_x_max, n_points)
    secondary_x_common = np.linspace(secondary_x_min, secondary_x_max, n_points)

    a_primary_y = np.interp(
        primary_x_common,
        a_primary[a_primary_idx, 0],
        a_primary[a_primary_idx, 1],
    )
    a_secondary_y = np.interp(
        secondary_x_common,
        a_secondary[a_secondary_idx, 0],
        a_secondary[a_secondary_idx, 1],
    )
    b_primary_y = np.interp(
        primary_x_common,
        b_primary[b_primary_idx, 0],
        b_primary[b_primary_idx, 1],
    )
    b_secondary_y = np.interp(
        secondary_x_common,
        b_secondary[b_secondary_idx, 0],
        b_secondary[b_secondary_idx, 1],
    )

    primary_y_combined = a_primary_y - b_primary_y
    secondary_y_combined = a_secondary_y - b_secondary_y

    total_points = 2 * n_points
    combined = np.empty((total_points, 3))

    combined[:n_points, 0] = primary_x_common
    combined[:n_points, 1] = primary_y_combined
    combined[:n_points, 2] = 1

    combined[n_points:, 0] = secondary_x_common[::-1]
    combined[n_points:, 1] = secondary_y_combined[::-1]
    combined[n_points:, 2] = -1

    return ratio, combined
