"""
Time-related utility functions
"""

import datetime
import pandas as pd
import pandas_market_calendars as mcal
from datetime import timedelta
import pytz
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def millis_to_datetime(ts: int) -> datetime.datetime:
    """
    convert milliseconds to datetime

    args:
        ts: int: The timestamp in milliseconds.
    """
    return datetime.datetime.fromtimestamp(ts / 1000.0, tz=pytz.UTC)


def count_trading_days(start_date: str, end_date: str) -> int:
    """
    count trading days between two given dates using the NYSE calendar INCLUSIVE

    Args:
        start_date: Start date in string format (e.g., "2024-01-01")
        end_date: End date in string format (e.g., "2024-01-31")

    Returns:
        int: Number of trading days between start_date and end_date (inclusive)
    """
    # Get the NYSE calendar
    nyse = mcal.get_calendar("NYSE")
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Calculate trading days between the two dates
    days = len(nyse.valid_days(start_date=start_date, end_date=end_date))

    return days


def closest_trading_day(date: str) -> str:
    """
    get the closest prior trading day to the given date (which may not be a trading day)

    args:
        date: str: The date to find the closest trading day to.
    """
    nyse = mcal.get_calendar("NYSE")
    date_ts = pd.Timestamp(date)
    closest = nyse.valid_days(start_date=date_ts - timedelta(days=7), end_date=date_ts)[
        -1
    ]  # assumes we wont get a whole week off
    return closest.strftime("%Y-%m-%d")


def closest_trading_day_now() -> str:
    """
    Get the closest trading day from now, considering market open hours.

    Returns:
        str: The closest trading day in YYYY-MM-DD format.
    """
    now = pd.Timestamp.now(tz="UTC")
    today_str = datetime.datetime.strftime(now, "%Y-%m-%d")

    if is_trading_day(today_str):
        # if pre-market open, use the previous trading day; market ends at 21:00 UTC
        if now.hour < 14 or (now.hour == 14 and now.minute < 30):
            return prev_trading_day(today_str)
        else:
            return today_str

    else:
        return closest_trading_day(today_str)


def is_trading_day(date: str) -> bool:
    """
    Check if the given date is a trading day on the NYSE.

    Args:
        date (str): The date to check (format 'YYYY-MM-DD').

    Returns:
        bool: True if it's a trading day, False otherwise.
    """
    nyse = mcal.get_calendar("NYSE")
    date_ts = pd.Timestamp(date)
    valid_days = nyse.valid_days(start_date=date_ts, end_date=date_ts)
    return not valid_days.empty and valid_days[0].strftime("%Y-%m-%d") == date


def prev_trading_day(date: str) -> str:
    """
    get the previous trading day to the given trading date

    args:
        date: str: The date to find the previous trading day to.
    """
    nyse = mcal.get_calendar("NYSE")
    date = pd.Timestamp(date)
    prev = nyse.valid_days(start_date=date - timedelta(days=7), end_date=date)[-2]
    return prev.strftime("%Y-%m-%d")


def trading_day_range(start: str, end: str) -> list:
    """
    get the trading days between the start and end dates

    args:
        start: str: The start date.
        end: str: The end date.
    """
    nyse = mcal.get_calendar("NYSE")
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return nyse.valid_days(start_date=start, end_date=end).strftime("%Y-%m-%d")


def get_date_range_utc(
    start_date: str, end_date: str, timezone: Optional[str] = None
) -> tuple[str, str]:
    """Convert local date range to UTC datetime range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        timezone: User's timezone (e.g. 'America/New_York'). If None, uses UTC.

    Returns:
        Tuple of (start_datetime, end_datetime) in UTC
    """
    # Parse dates
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    if timezone:
        # Convert to user's timezone first
        local_tz = pytz.timezone(timezone)
        start = local_tz.localize(start)
        end = local_tz.localize(end.replace(hour=23, minute=59, second=59))

        # Convert to UTC
        start = start.astimezone(pytz.UTC)
        end = end.astimezone(pytz.UTC)
    else:
        # Use UTC
        start = pytz.UTC.localize(start)
        end = pytz.UTC.localize(end.replace(hour=23, minute=59, second=59))

    return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")


def seconds_since_mkt_open(timestamp: int) -> int:
    """
    Get the number of seconds since the market opened for a given timestamp.

    Args:
        timestamp: int: The timestamp in milliseconds since epoch

    Returns:
        int: Number of seconds since market open. If market is not yet open, returns negative value.
    """
    # Convert timestamp to UTC datetime
    dt_utc = millis_to_datetime(timestamp)

    # Convert to Eastern time where market hours are based
    eastern = pytz.timezone("America/New_York")
    dt_eastern = dt_utc.astimezone(eastern)

    # Get market open time (9:30 AM ET) for the same day
    market_open = eastern.localize(
        datetime.datetime.combine(dt_eastern.date(), datetime.time(hour=9, minute=30))
    )

    # Convert market open back to UTC for consistent comparison
    market_open_utc = market_open.astimezone(pytz.UTC)

    # Calculate seconds difference
    return int((dt_utc - market_open_utc).total_seconds())


def next_trading_day(date: str, n: int = 1) -> str:
    """
    Get the next N trading days from the given date

    Args:
        date: str: The starting date in YYYY-MM-DD format
        n: int: The number of trading days to advance (default 1)
                - If input date is not a trading day, first moves to closest trading day
                - Then adds n more trading days from that point
                - If n=0, returns the closest trading day to input date

    Returns:
        str: The resulting date in YYYY-MM-DD format

    Example:
        >>> next_trading_day("2024-01-01", 1)  # Monday -> Tuesday
        "2024-01-02"
        >>> next_trading_day("2024-01-06", 1)  # Saturday -> Monday + 1 = Tuesday
        "2024-01-09"
        >>> next_trading_day("2024-01-06", 0)  # Saturday -> Monday
        "2024-01-08"
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    nyse = mcal.get_calendar("NYSE")
    date_ts = pd.Timestamp(date)

    # Step 1: Normalize input date to a trading day
    if is_trading_day(date):
        start_trading_date = date
        start_trading_ts = date_ts
    else:
        # Find the next trading day after the input date
        trading_days = nyse.valid_days(
            start_date=date_ts + timedelta(days=1),
            end_date=date_ts + timedelta(days=10),  # Look ahead up to 10 calendar days
        )
        if len(trading_days) == 0:
            raise ValueError(f"No trading days found after {date}")
        start_trading_date = trading_days[0].strftime("%Y-%m-%d")
        start_trading_ts = trading_days[0]

    # Step 2: Handle n=0 case - return the normalized trading day
    if n == 0:
        return start_trading_date

    # Step 3: Add n more trading days from the normalized starting point
    # Look ahead enough calendar days to ensure we get enough trading days
    look_ahead_days = max(n * 2, 14)  # At least 2 weeks to handle holidays

    trading_days = nyse.valid_days(
        start_date=start_trading_ts + timedelta(days=1),
        end_date=start_trading_ts + timedelta(days=look_ahead_days),
    )

    if len(trading_days) < n:
        # If we don't have enough trading days, look further ahead
        look_ahead_days = n * 3  # Extend the search range
        trading_days = nyse.valid_days(
            start_date=start_trading_ts + timedelta(days=1),
            end_date=start_trading_ts + timedelta(days=look_ahead_days),
        )

    if len(trading_days) < n:
        raise ValueError(f"Could not find {n} trading days after {start_trading_date}")

    # Return the nth trading day (1-indexed)
    return trading_days[n - 1].strftime("%Y-%m-%d")
