# SPDX-FileCopyrightText: 2024-2026 Stanford University
# SPDX-License-Identifier: AGPL-3.0-or-later

# steer_core/Mixins/DateTime.py
"""
steer_core/Mixins/DateTime.py

Lightweight, dependency-free datetime parsing and validation helpers.

Goal:
- Provide shared utilities across STEER repos for parsing user-friendly datetime strings
  into canonical `datetime` objects with enforced alignment (hour/day).
"""

from __future__ import annotations

import calendar
from datetime import datetime
from typing import Optional

from steer_core.Constants.Format import DEFAULT_HOUR_FMT, DEFAULT_DAY_FMT


class DateTimeMixin:
    """
    A mixin class to handle datetime parsing, validation, and alignment operations.
    Provides utilities for converting strings to datetime objects with enforced temporal alignment.
    """

    @staticmethod
    def str_to_datetime(value: str, *, fmt: Optional[str] = None) -> datetime:
        """Parse a datetime string using a provided strptime format.

        If no format is specified, automatically detects and parses using either
        the hour format ('%Y-%m-%d-%H') or day format ('%Y-%m-%d').

        Args:
            value: The datetime string to parse.
            fmt: The strptime format string (e.g., '%Y-%m-%d-%H').
                If None, automatically tries both DEFAULT_HOUR_FMT and DEFAULT_DAY_FMT.

        Returns:
            The parsed datetime object.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value cannot be parsed with the provided or detected format(s).

        Examples:
            >>> DateTimeMixin.str_to_datetime('2024-01-15-14')
            datetime.datetime(2024, 1, 15, 14, 0, 0)
            >>> DateTimeMixin.str_to_datetime('2024-01-15')
            datetime.datetime(2024, 1, 15, 0, 0, 0)
        """
        if not isinstance(value, str):
            fmt_msg = fmt if fmt else f"'{DEFAULT_HOUR_FMT}' or '{DEFAULT_DAY_FMT}'"
            raise TypeError(f"value must be a string matching format {fmt_msg}")

        # If format is specified, use it directly
        if fmt is not None:
            try:
                return datetime.strptime(value, fmt)
            except ValueError as e:
                raise ValueError(f"value must match format '{fmt}' (got '{value}')") from e
        
        # Auto-detect format: try hour format first, then day format
        for try_fmt in [DEFAULT_HOUR_FMT, DEFAULT_DAY_FMT]:
            try:
                return datetime.strptime(value, try_fmt)
            except ValueError:
                continue
        
        # If neither format worked, raise an error
        raise ValueError(
            f"value must match format '{DEFAULT_HOUR_FMT}' or '{DEFAULT_DAY_FMT}' (got '{value}')"
        )

    @staticmethod
    def datetime_to_str(dt: datetime, *, fmt: Optional[str] = None) -> str:
        """Format a datetime object into a user-friendly string.

        If no format is specified, uses the hour format ('%Y-%m-%d-%H').

        Args:
            dt: The datetime object to format.
            fmt: The strftime format string (e.g., '%Y-%m-%d-%H', '%Y-%m-%d').
                If None, defaults to DEFAULT_HOUR_FMT.

        Returns:
            The formatted datetime string.

        Raises:
            TypeError: If dt is not a datetime object.

        Examples:
            >>> dt = datetime(2024, 1, 15, 14, 0, 0)
            >>> DateTimeMixin.datetime_to_str(dt)
            '2024-01-15-14'
        """
        if not isinstance(dt, datetime):
            raise TypeError("dt must be a datetime object")

        # If format is specified, use it directly
        if fmt is not None:
            return dt.strftime(fmt)
        
        # Default to hour format
        return dt.strftime(DEFAULT_HOUR_FMT)


    @staticmethod
    def shift_years(dt: datetime, years: int) -> datetime:
        """Shift a datetime by a specified number of years (forward or backward).

        Handles the edge case of February 29 (leap day): if the original date is
        Feb 29 and the target year is not a leap year, the result will be Feb 28.

        Args:
            dt: The datetime object to shift.
            years: The number of years to shift (positive to add, negative to subtract).

        Returns:
            A new datetime object with the years shifted.

        Raises:
            TypeError: If dt is not a datetime object or years is not an integer.

        Examples:
            >>> dt = datetime(2026, 2, 2, 14, 0, 0)
            >>> DateTimeMixin.shift_years(dt, 2)
            datetime.datetime(2028, 2, 2, 14, 0, 0)
        """
        if not isinstance(dt, datetime):
            raise TypeError("dt must be a datetime object")
        if not isinstance(years, int):
            raise TypeError("years must be an integer")

        target_year = dt.year + years
        
        # Try to create the new datetime with the target year
        try:
            return dt.replace(year=target_year)
        except ValueError:
            # This happens when the original date is Feb 29 and target year is not a leap year
            # Fall back to Feb 28
            return dt.replace(year=target_year, day=28)


    @staticmethod
    def shift_months(dt: datetime, months: int) -> datetime:
        """Shift a datetime by a specified number of months (forward or backward).

        Handles month boundaries intelligently: if the original day doesn't exist in
        the target month (e.g., Jan 31 + 1 month), the result will be the last valid
        day of that month (e.g., Feb 28 or Feb 29).

        Args:
            dt: The datetime object to shift.
            months: The number of months to shift (positive to add, negative to subtract).

        Returns:
            A new datetime object with the months shifted.

        Raises:
            TypeError: If dt is not a datetime object or months is not an integer.

        Examples:
            >>> dt = datetime(2026, 2, 2, 14, 0, 0)
            >>> DateTimeMixin.shift_months(dt, 2)
            datetime.datetime(2026, 4, 2, 14, 0, 0)
        """
        if not isinstance(dt, datetime):
            raise TypeError("dt must be a datetime object")
        if not isinstance(months, int):
            raise TypeError("months must be an integer")

        # Calculate target month and year
        total_months = dt.month + months
        target_year = dt.year + (total_months - 1) // 12
        target_month = ((total_months - 1) % 12) + 1

        # Get the last day of the target month
        _, last_day_of_month = calendar.monthrange(target_year, target_month)

        # Use the minimum of original day and last day of target month
        target_day = min(dt.day, last_day_of_month)

        return dt.replace(year=target_year, month=target_month, day=target_day)


    @staticmethod
    def validate_end_after_start(start: datetime, end: datetime, *, strictly: bool = True) -> None:
        """Validate that end datetime comes after start datetime.

        Args:
            start: The start datetime.
            end: The end datetime.
            strictly: If True, end must be strictly after start (end > start).
                If False, end can equal start (end >= start). Default is True.

        Raises:
            TypeError: If start or end is not a datetime object.
            ValueError: If end is not after start.

        Examples:
            >>> start = datetime(2024, 1, 15, 10, 0, 0)
            >>> end = datetime(2024, 1, 15, 14, 0, 0)
            >>> DateTimeMixin.validate_end_after_start(start, end)  # OK
        """
        if not isinstance(start, datetime):
            raise TypeError("start must be a datetime")
        if not isinstance(end, datetime):
            raise TypeError("end must be a datetime")
        
        if strictly:
            if end <= start:
                raise ValueError(f"end ({end}) must be strictly after start ({start})")
        else:
            if end < start:
                raise ValueError(f"end ({end}) must be after or equal to start ({start})")
    

    
