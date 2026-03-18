# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Generic utilities for multi-mode dependent property dispatch.

When N properties are interdependent and only N-1 can be independently set,
use a control mode enum to select which property stays fixed.  The
:func:`dispatch_dependent_update` function routes property changes to the
correct recalculation function based on the active mode.
"""

from enum import Enum
from typing import Any, Callable, Dict, Tuple


def dispatch_dependent_update(
    mode: Enum,
    property_name: str,
    dependency_map: Dict[Enum, Dict[str, Callable]],
    input_map: Dict[Enum, Dict[str, Tuple[Any, ...]]],
) -> Any:
    """Route a property change to the correct recalculation function.

    Parameters
    ----------
    mode : Enum
        The active control mode.
    property_name : str
        The name of the property that just changed.
    dependency_map : dict
        Nested mapping ``{mode: {property_name: callable}}`` where the
        callable is the function to execute when *property_name* changes
        under *mode*.
    input_map : dict
        Nested mapping ``{mode: {property_name: tuple_of_args}}`` providing
        the arguments to pass to the callable.

    Returns
    -------
    Any
        The return value of the dispatched function.

    Raises
    ------
    KeyError
        If *mode* or *property_name* is not found in the maps.
    """
    func = dependency_map[mode][property_name]
    args = input_map[mode][property_name]
    return func(*args)
