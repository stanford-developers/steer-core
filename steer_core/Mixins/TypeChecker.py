# SPDX-FileCopyrightText: 2024-2026 Nicholas Siemons
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations

from typing import Type, Iterable
from enum import Enum
from datetime import datetime
import pandas as pd
import numpy as np

from steer_core.Constants.Format import DEFAULT_HOUR_FMT, DEFAULT_DAY_FMT
from steer_core.Utils import is_plotly_trace as _is_plotly_trace


class ValidationMixin:

    @staticmethod
    def validate_plotly_trace(value: object, name: str) -> bool:
        """Check whether *value* is a Plotly trace object.

        Args:
            value: The value to validate.
            name: The name of the parameter (unused, kept for API compatibility).

        Returns:
            ``True`` if *value* is a Plotly trace, ``False`` otherwise.
        """
        return _is_plotly_trace(value)
        
    @staticmethod
    def validate_type(value, expected_type, name: str) -> None:
        """Validate that a value is of the expected type or one of multiple allowed types.

        Args:
            value: The value to validate.
            expected_type: A single expected type or an iterable (list/tuple/set) of acceptable types.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is not an instance of any of the expected types.

        Examples:
            >>> ValidationMixin.validate_type(5, int, 'count')            # OK
            >>> ValidationMixin.validate_type(5, (int, float), 'count')   # OK
            >>> ValidationMixin.validate_type('x', (int, float), 'count') # TypeError
            >>> ValidationMixin.validate_type([1,2,3], list, 'items')     # OK
            >>> ValidationMixin.validate_type([1,2,3], [list, tuple], 'items') # OK
        """
        # Normalize expected types to a tuple for isinstance
        if isinstance(expected_type, (list, set)):
            expected_types = tuple(expected_type)
        elif isinstance(expected_type, tuple):
            expected_types = expected_type
        else:
            expected_types = (expected_type,)

        if not isinstance(value, expected_types):
            type_names = ', '.join(t.__name__ for t in expected_types)
            raise TypeError(f"{name} must be of type {type_names}. Provided: {type(value).__name__}.")

    @staticmethod
    def validate_percentage(value: float, name: str) -> None:
        """Validate that a value is a percentage (between 0 and 100).

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.

        Raises:
            ValueError: If the value is not a percentage.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number. Provided: {value}.")

        if not (0 <= value <= 100):
            raise ValueError(
                f"{name} must be a percentage between 0 and 100. Provided: {value}."
            )

    @staticmethod
    def validate_fraction(value: float, name: str) -> None:
        """Validate that a value is a fraction (between 0 and 1).

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.

        Raises:
            ValueError: If the value is not a fraction.
        """
        if not (0 <= value <= 1):
            raise ValueError(
                f"{name} must be a fraction between 0 and 1. Provided: {value}."
            )

    @staticmethod
    def validate_pandas_dataframe(
        df: pd.DataFrame, name: str, column_names: list | None = None
    ) -> None:
        """Validate that the input is a pandas DataFrame.

        Args:
            df: The DataFrame to validate.
            name: The name of the DataFrame for error messages.

        Raises:
            TypeError: If the input is not a pandas DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{name} must be a pandas DataFrame. Provided: {type(df)}.")

        if column_names is not None:
            missing_columns = [col for col in column_names if col not in df.columns]
            if missing_columns:
                raise ValueError(
                    f"{name} is missing required columns: {missing_columns}. "
                    f"Available columns: {df.columns.tolist()}."
                )

    @staticmethod
    def validate_datum(datum: np.ndarray) -> None:
        """Validate the datum point for extrusion.

        Args:
            datum: Datum point for extrusion (shape (3,)).

        Raises:
            ValueError: If the datum does not have exactly 3 coordinates.
        """
        if not isinstance(datum, (tuple, list, np.ndarray)) or len(datum) != 3:
            raise ValueError("Datum must be a 3D point with exactly 3 coordinates.")

        if not all(isinstance(coord, (int, float)) for coord in datum):
            raise TypeError("All coordinates in datum must be numbers.")

    @staticmethod
    def validate_positive_float(value: float, name: str) -> None:
        """Validate that a value is a positive float.

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.

        Raises:
            ValueError: If the value is not a positive float.
        """
        if not isinstance(value, (int, float, np.int64, np.float64)):
            raise TypeError(f"{name} must be a number. Provided: {type(value).__name__}.")
        if value < 0:
            raise ValueError(f"{name} must be a positive float. Provided: {value}.")

    @staticmethod
    def validate_positive_int(value: int, name: str, strictly: bool = True) -> None:
        """Validate that a value is a positive integer.

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.
            strictly: If True (default), value must be strictly positive (> 0).
                If False, value must be non-negative (>= 0).

        Raises:
            TypeError: If the value is not an integer (bool is rejected even though it is a subclass of int).
            ValueError: If the integer does not meet the positivity requirement.

        Examples:
            >>> ValidationMixin.validate_positive_int(5, 'count')              # OK
            >>> ValidationMixin.validate_positive_int(0, 'count')              # ValueError (strict mode)
            >>> ValidationMixin.validate_positive_int(0, 'count', strictly=False)  # OK (non-strict mode)
            >>> ValidationMixin.validate_positive_int(-3, 'count')             # ValueError
            >>> ValidationMixin.validate_positive_int(True, 'flag')            # TypeError (bool rejected)
            >>> ValidationMixin.validate_positive_int(12_000, 'cycles')        # OK
        """
        # Reject bool explicitly (bool is subclass of int)
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer. Provided: {value} (type: {type(value).__name__}).")

        if strictly:
            if value <= 0:
                raise ValueError(f"{name} must be a strictly positive integer (> 0). Provided: {value}.")
        else:
            if value < 0:
                raise ValueError(f"{name} must be a non-negative integer (>= 0). Provided: {value}.")

    @staticmethod
    def validate_string(value: str, name: str) -> None:
        """Validate that a value is a string.

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is not a string.
        """
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string. Provided: {value}.")

    @staticmethod
    def validate_two_iterable_of_floats(value: tuple, name: str) -> None:
        """Validate that a value is a tuple of two iterables.

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is not a tuple of two floats.
        """
        # Accept both tuples and lists
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise TypeError(
                f"{name} must be a tuple or list of two numbers. Provided: {value}."
            )

        # Check if all values are numeric (int or float)
        if not all(isinstance(v, (int, float)) for v in value):
            raise TypeError(
                f"{name} must be a tuple or list of two numbers. Provided: {value}."
            )

        # Check if all values are non-negative
        if not all(v >= 0 for v in value):
            raise ValueError(
                f"{name} must be a tuple or list of two non-negative numbers. Provided: {value}."
            )

    @staticmethod
    def validate_positive_float_list(value: list, name: str) -> None:
        """Validate that a value is a list of positive floats.

        Args:
            value: The value to validate.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is not a list of positive floats.
        """
        if not isinstance(value, list) or not all(
            isinstance(v, (int, float)) and v > 0 for v in value
        ):
            raise TypeError(
                f"{name} must be a list of positive floats. Provided: {value}."
            )

        if len(value) == 0:
            raise ValueError(f"{name} must not be an empty list. Provided: {value}.")

    @staticmethod
    def validate_enum_string(value, enum_class: Type[Enum], name: str) -> None:
        """Validate that a string value belongs to an enum class.

        Args:
            value: The string value to validate.
            enum_class: The enum class to validate against.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is not a string.
            ValueError: If the string value is not a valid member of the enum class.

        Examples:
            >>> from enum import Enum
            >>> class AllocationShape(Enum):
            ...     CIRCLE = 'circle'
            ...     SQUARE = 'square'
            >>> ValidationMixin.validate_enum_string('circle', AllocationShape, 'shape')  # OK
            >>> ValidationMixin.validate_enum_string('triangle', AllocationShape, 'shape')  # Raises ValueError
        """
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string. Provided: {type(value).__name__}.")
        
        try:
            enum_class(value)
        except ValueError as e:
            raise ValueError(
                f"{name} must be one of {[member.value for member in enum_class]}"
            ) from e

    @staticmethod
    def validate_datetime_string(value: str, name: str) -> None:
        """Validate that a string is in a valid datetime format.

        Accepts either 'YYYY-MM-DD-HH' (hourly) or 'YYYY-MM-DD' (daily) formats.

        Args:
            value: The datetime string to validate.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is not a string.
            ValueError: If the string is not in a valid datetime format.

        Examples:
            >>> ValidationMixin.validate_datetime_string('2024-01-15-14', 'start_dt')  # OK
            >>> ValidationMixin.validate_datetime_string('2024-01-15', 'start_dt')     # OK
            >>> ValidationMixin.validate_datetime_string('2024/01/15', 'start_dt')     # Raises ValueError
        """
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string. Provided: {type(value).__name__}.")
        
        # Try both formats
        formats = [DEFAULT_HOUR_FMT, DEFAULT_DAY_FMT]
        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return  # Valid format found
            except ValueError:
                continue
        
        # If none of the formats worked, raise an error
        raise ValueError(
            f"{name} must be in format 'YYYY-MM-DD-HH' or 'YYYY-MM-DD'. Provided: {value}."
        )

    @staticmethod
    def validate_number(value, name: str) -> None:
        """Validate that a value is a numeric amount (int or float, but not bool).

        Args:
            value: The numeric value to validate.
            name: The name of the parameter for error messages.

        Raises:
            TypeError: If the value is a bool or not a numeric type (int or float).

        Examples:
            >>> ValidationMixin.validate_number(42, 'amount')      # OK
            >>> ValidationMixin.validate_number(3.14, 'amount')    # OK
            >>> ValidationMixin.validate_number(True, 'amount')    # Raises TypeError
            >>> ValidationMixin.validate_number('100', 'amount')   # Raises TypeError
        """
        if isinstance(value, bool):
            raise TypeError(f"{name} must be a number (int or float), not bool.")
        
        if not isinstance(value, (int, float, np.int64)):
            raise TypeError(f"{name} must be a number (int or float). Provided: {type(value).__name__}.")

