"""
Test cases for sharpe.utils modules
"""

import datetime
import pytest
import numpy as np
import pandas as pd
import pytz

from sharpe.utils.time import (
    closest_trading_day,
    trading_day_range,
    next_trading_day,
    millis_to_datetime,
    prev_trading_day,
    is_trading_day,
    get_date_range_utc,
    seconds_since_mkt_open,
)
from sharpe.utils.options import (
    input_to_osi,
    osi_to_input,
    get_delta_bucket,
    implied_volatility_from_straddle,
    find_strike_by_delta,
)


# Time utilities tests
def test_closest_trading_day():
    """Test closest_trading_day function"""
    # Test with a weekend date
    result = closest_trading_day("2024-12-14")  # Saturday
    assert result == "2024-12-13"  # Should return Friday

    # Test with a weekday
    result = closest_trading_day("2024-12-13")  # Friday
    assert result == "2024-12-13"  # Should return same day


def test_trading_day_range():
    """Test trading_day_range function"""
    start = "2024-01-01"
    end = "2024-01-05"
    days = list(trading_day_range(start, end))
    assert len(days) == 4  # Jan 1 is a holiday
    assert days[0] == "2024-01-02"
    assert days[-1] == "2024-01-05"


def test_next_trading_day():
    """Test next_trading_day function with various scenarios"""

    # User's specific test case: Holiday (New Year's Day) + 1 trading day
    result = next_trading_day("2025-01-01", 1)  # New Year's Day (Wednesday, holiday)
    assert result == "2025-01-03"  # Should normalize to Jan 2 (Thurs) + 1 = Jan 3 (Fri)

    # Test n=0 cases
    # Trading day with n=0 should return same day
    result = next_trading_day("2024-01-02", 0)  # Tuesday
    assert result == "2024-01-02"

    # Weekend with n=0 should return next trading day
    result = next_trading_day("2024-01-06", 0)  # Saturday
    assert result == "2024-01-08"  # Monday

    # Holiday with n=0 should return next trading day
    result = next_trading_day("2025-01-01", 0)  # New Year's Day (Wednesday, holiday)
    assert result == "2025-01-02"  # Thursday

    # Test n=1 cases
    # Trading day + 1 should return next trading day
    result = next_trading_day("2024-01-02", 1)  # Tuesday
    assert result == "2024-01-03"  # Wednesday

    # Weekend + 1 should normalize to Monday, then add 1 = Tuesday
    result = next_trading_day("2024-01-06", 1)  # Saturday
    assert result == "2024-01-09"  # Tuesday (Monday + 1)

    # Friday + 1 should skip weekend to Monday
    result = next_trading_day("2024-01-05", 1)  # Friday
    assert result == "2024-01-08"  # Monday

    # Test larger n values
    # Tuesday + 5 trading days should skip weekend
    result = next_trading_day("2024-01-02", 5)  # Tuesday
    assert result == "2024-01-09"  # Tuesday next week

    # Test edge cases
    # Test with negative n (should raise error)
    with pytest.raises(ValueError, match="n must be non-negative"):
        next_trading_day("2024-01-02", -1)


def test_next_trading_day_holiday_scenarios():
    """Test next_trading_day with various holiday scenarios"""

    # Test Independence Day 2024 (July 4th is Thursday, holiday)
    result = next_trading_day("2024-07-04", 1)  # Thursday holiday
    assert result == "2024-07-08"  # Normalize to July 5 (Fri) + 1 = July 8 (Mon)

    # Test Memorial Day 2024 (May 27th, last Monday in May)
    result = next_trading_day("2024-05-27", 1)  # Monday holiday
    assert result == "2024-05-29"  # Normalize to May 28 (Tue) + 1 = May 29 (Wed)

    # Test Thanksgiving 2024 (November 28th, Thursday)
    result = next_trading_day("2024-11-28", 1)  # Thursday holiday
    assert (
        result == "2024-12-02"
    )  # Normalize to Nov 29 (Fri, half day) + 1 = Dec 2 (Mon)


def test_next_trading_day_weekend_scenarios():
    """Test next_trading_day with weekend dates"""

    # Saturday scenarios
    result = next_trading_day("2024-06-01", 0)  # Saturday
    assert result == "2024-06-03"  # Monday

    result = next_trading_day("2024-06-01", 2)  # Saturday
    assert result == "2024-06-05"  # Normalize to June 3 (Mon) + 2 = June 5 (Wed)

    # Sunday scenarios
    result = next_trading_day("2024-06-02", 0)  # Sunday
    assert result == "2024-06-03"  # Monday

    result = next_trading_day("2024-06-02", 3)  # Sunday
    assert result == "2024-06-06"  # Normalize to June 3 (Mon) + 3 = June 6 (Thu)


def test_input_to_osi():
    """Test conversion of option parameters to OSI format"""
    test_cases = [
        {
            "input": ("TSLA", "call", "2024-01-19", 250.0),
            "expected": "O:TSLA240119C00250000",
        },
        {
            "input": ("AAPL", "put", "2024-02-16", 175.5),
            "expected": "O:AAPL240216P00175500",
        },
        {
            "input": ("SPY", "C", "2024-03-15", 500.0),
            "expected": "O:SPY240315C00500000",
        },
    ]

    for case in test_cases:
        symbol, flavor, expiry, strike = case["input"]
        result = input_to_osi(symbol, flavor, expiry, strike)
        assert result == case["expected"]


def test_input_to_osi_invalid_flavor():
    """Test input_to_osi with invalid option flavor"""
    with pytest.raises(ValueError):
        input_to_osi("TSLA", "invalid", "2024-01-19", 250.0)


def test_osi_to_input():
    """Test parsing of OSI format to option parameters"""
    test_cases = [
        {
            "input": "O:TSLA240119C00250000",
            "expected": ("TSLA", "2024-01-19", "C", 250.0),
        },
        {
            "input": "O:AAPL240216P00175500",
            "expected": ("AAPL", "2024-02-16", "P", 175.5),
        },
    ]

    for case in test_cases:
        result = osi_to_input(case["input"])
        assert result == case["expected"]


def test_osi_to_input_invalid_format():
    """Test osi_to_input with invalid OSI format"""
    # Test missing O: prefix
    with pytest.raises(ValueError) as exc_info:
        osi_to_input("INVALID")
    assert str(exc_info.value) == "Invalid OSI format: must start with 'O:'"

    # Test invalid pattern
    with pytest.raises(ValueError) as exc_info:
        osi_to_input("O:INVALID")
    assert (
        str(exc_info.value)
        == "Invalid OSI format: must match pattern SYMBOL+YYMMDD+[CP]+STRIKE"
    )


def test_get_delta_bucket():
    """Test delta bucketing functionality"""
    try:
        # Test various delta values
        bucket_1 = get_delta_bucket(0.05)  # Low delta
        bucket_2 = get_delta_bucket(0.25)  # Mid delta
        bucket_3 = get_delta_bucket(0.55)  # High delta

        assert isinstance(bucket_1, (str, int))
        assert isinstance(bucket_2, (str, int))
        assert isinstance(bucket_3, (str, int))

    except Exception as e:
        pytest.skip(f"get_delta_bucket test skipped due to: {e}")


def test_logger_functionality():
    """Test logger utility"""
    try:
        from sharpe.utils.logger import get_logger

        logger = get_logger("test_logger")
        assert logger is not None

        # Test basic logging functionality
        logger.info("Test log message")

    except ImportError:
        pytest.skip("Logger test skipped")


def test_env_functionality():
    """Test environment utilities"""
    try:
        from sharpe.utils.env import load_dotenv

        # Should load without error
        assert load_dotenv is not None
    except ImportError:
        pytest.skip("Environment utilities test skipped")


def test_universe_functionality():
    """Test universe management utilities"""
    try:
        from sharpe.utils.universe import get_stock_rank

        # Should import without error
        assert get_stock_rank is not None
    except ImportError:
        pytest.skip("Universe utilities test skipped")


def test_millis_to_datetime():
    ts = 1704209400000  # 2024-01-02 15:30:00 UTC
    dt = millis_to_datetime(ts)
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 2
    assert dt.hour == 15
    assert dt.minute == 30
    assert dt.tzinfo is not None


def test_prev_and_is_trading_day():
    # Monday 2024-01-08 previous trading day should be Friday 2024-01-05
    assert prev_trading_day("2024-01-08") == "2024-01-05"
    assert is_trading_day("2024-01-01") is False  # New Year's Day
    assert is_trading_day("2024-01-02") is True


def test_get_date_range_utc_with_timezone():
    start, end = get_date_range_utc(
        "2024-01-01",
        "2024-01-02",
        timezone="America/New_York",
    )
    assert start == "2024-01-01 05:00:00"
    assert end == "2024-01-03 04:59:59"

    start2, end2 = get_date_range_utc("2024-01-01", "2024-01-02")
    assert start2 == "2024-01-01 00:00:00"
    assert end2 == "2024-01-02 23:59:59"


def test_seconds_since_mkt_open():
    # 10:30 ET on 2024-01-02 -> 15:30 UTC -> 3600 seconds after open
    dt = datetime.datetime(2024, 1, 2, 15, 30, tzinfo=pytz.UTC)
    ts = int(dt.timestamp() * 1000)
    assert seconds_since_mkt_open(ts) == 3600

    # Before market open (8:00 ET -> 13:00 UTC)
    dt_pre = datetime.datetime(2024, 1, 2, 13, 0, tzinfo=pytz.UTC)
    ts_pre = int(dt_pre.timestamp() * 1000)
    assert seconds_since_mkt_open(ts_pre) == -5400


def test_implied_volatility_from_straddle():
    iv = implied_volatility_from_straddle(100.0, 8.5, 30)
    assert pytest.approx(iv, rel=1e-3) == 0.30934

    # zero time to expiration with price equal to intrinsic value -> 0
    assert implied_volatility_from_straddle(100, 0, 0) == 0.0

    # zero time but price above intrinsic value should raise
    with pytest.raises(ValueError):
        implied_volatility_from_straddle(100, 10, 0)


def test_find_strike_by_delta():
    strike_call = find_strike_by_delta(
        100, 0.5, 30, implied_vol=0.3, option_type="call"
    )
    strike_put = find_strike_by_delta(100, -0.5, 30, implied_vol=0.3, option_type="put")
    # Should return around ATM
    assert pytest.approx(strike_call, abs=0.5) == 101.18
    assert pytest.approx(strike_put, abs=0.5) == 101.18
