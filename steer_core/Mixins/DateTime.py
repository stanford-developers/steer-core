# steer_core/Mixins/DateTime.py
"""
steer_core/Mixins/DateTime.py

Lightweight, dependency-free datetime parsing and validation helpers.

Goal:
- Provide shared utilities across STEER repos for parsing user-friendly datetime strings
  into canonical `datetime` objects with enforced alignment (hour/day).
"""

from __future__ import annotations

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
        """
        Parse a datetime string using a provided strptime format.

        If no format is specified, automatically detects and parses using either
        the hour format ('%Y-%m-%d-%H') or day format ('%Y-%m-%d').

        Parameters
        ----------
        value : str
            The datetime string to parse.
        fmt : str, optional
            The strptime format string (e.g., '%Y-%m-%d-%H').
            If None, automatically tries both DEFAULT_HOUR_FMT and DEFAULT_DAY_FMT.

        Returns
        -------
        datetime
            The parsed datetime object.

        Raises
        ------
        TypeError
            If value is not a string.
        ValueError
            If value cannot be parsed with the provided or detected format(s).

        Examples
        --------
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
        """
        Format a datetime object into a user-friendly string.

        If no format is specified, uses the hour format ('%Y-%m-%d-%H').

        Parameters
        ----------
        dt : datetime
            The datetime object to format.
        fmt : str, optional
            The strftime format string (e.g., '%Y-%m-%d-%H', '%Y-%m-%d').
            If None, defaults to DEFAULT_HOUR_FMT.

        Returns
        -------
        str
            The formatted datetime string.

        Raises
        ------
        TypeError
            If dt is not a datetime object.

        Examples
        --------
        >>> dt = datetime(2024, 1, 15, 14, 0, 0)
        >>> DateTimeMixin.datetime_to_str(dt)
        '2024-01-15-14'
        >>> dt = datetime(2024, 1, 15, 0, 0, 0)
        >>> DateTimeMixin.datetime_to_str(dt)
        '2024-01-15-00'
        """
        if not isinstance(dt, datetime):
            raise TypeError("dt must be a datetime object")

        # If format is specified, use it directly
        if fmt is not None:
            return dt.strftime(fmt)
        
        # Default to hour format
        return dt.strftime(DEFAULT_HOUR_FMT)

    @staticmethod
    def validate_end_after_start(start: datetime, end: datetime, *, strictly: bool = True) -> None:
        """
        Validate that end datetime comes after start datetime.

        Parameters
        ----------
        start : datetime
            The start datetime.
        end : datetime
            The end datetime.
        strictly : bool, optional
            If True, end must be strictly after start (end > start).
            If False, end can equal start (end >= start).
            Default is True.

        Raises
        ------
        TypeError
            If start or end is not a datetime object.
        ValueError
            If end is not after start (or not >= start if strictly=False).

        Examples
        --------
        >>> start = datetime(2024, 1, 15, 10, 0, 0)
        >>> end = datetime(2024, 1, 15, 14, 0, 0)
        >>> DateTimeMixin.validate_end_after_start(start, end)  # OK
        >>> DateTimeMixin.validate_end_after_start(start, start)  # Raises ValueError
        >>> DateTimeMixin.validate_end_after_start(start, start, strictly=False)  # OK
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
