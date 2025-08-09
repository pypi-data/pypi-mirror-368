"""
get the universe for stock / options
"""

import datetime
from typing import List, Optional, Union, Dict, Any

import pandas as pd

from ..data import mkt
from ..data import db
from .time import closest_trading_day_now, closest_trading_day, prev_trading_day
from .logger import get_logger

logger = get_logger(__name__)


def _get_stock_daily_data(
    date: Optional[str] = None,
    columns: Optional[List[str]] = None,
    retry_on_empty: bool = True,
) -> pd.DataFrame:
    """
    Helper function to get stock daily data from the database.

    Args:
        date: Date to query for in YYYY-MM-DD format. If None, uses the latest available date.
        columns: List of columns to select. If None, selects all columns.
        retry_on_empty: Whether to retry with the previous trading day if no data is found.

    Returns:
        DataFrame containing the requested stock data.
    """
    try:
        # Determine columns to select
        cols_str = "*"
        if columns:
            cols_str = ", ".join(columns)

        # Build SQL query based on whether date is provided
        if not date:
            sql = f"""
                SELECT {cols_str}
                FROM stock_grouped_daily
                WHERE date = (SELECT MAX(date) FROM stock_grouped_daily)
            """
        else:
            sql = f"""
                SELECT {cols_str}
                FROM stock_grouped_daily
                WHERE date = '{date}'
            """

        # Execute the query
        df = db.read(sql)

        # Handle empty results
        if df.empty and retry_on_empty and date:
            logger.warning(f"No data found for date: {date}")
            prev_date = prev_trading_day(date)
            logger.info(f"Trying previous trading day: {prev_date}")
            return _get_stock_daily_data(prev_date, columns, retry_on_empty)

        return df

    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()


def get_top_n_traded_stock(date: Optional[str] = None, n: int = 100) -> List[str]:
    """
    Return top n traded stock by notional traded for the given date.

    Args:
        date: Date in YYYY-MM-DD format. If None, uses the latest available date.
        n: Number of top stocks to return.

    Returns:
        List of ticker symbols for the top n traded stocks.
    """
    # Get only the columns we need for this calculation
    df = _get_stock_daily_data(date, columns=["ticker", "date", "volume", "vwap"])

    if df.empty:
        return []

    # Calculate notional traded
    df["notional_traded"] = df["vwap"] * df["volume"]
    df = df.sort_values("notional_traded", ascending=False)
    return df["ticker"].head(n).to_list()


def get_stock_rank(date: Optional[str] = None, n: int = 500) -> pd.DataFrame:
    """
    Return stock rank by notional traded for the given date.

    Args:
        date: Date in YYYY-MM-DD format. If None, uses the latest available date.
        n: Number of top stocks to rank.

    Returns:
        DataFrame with ticker and rank columns.
    """
    # Get only the columns we need for this calculation
    df = _get_stock_daily_data(date, columns=["ticker", "volume", "vwap"])

    if df.empty:
        return pd.DataFrame(columns=["ticker", "rank"])

    # Calculate notional traded and rank
    df["notional_traded"] = df["vwap"] * df["volume"]
    df = df.sort_values("notional_traded", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    df["rank"] = df["rank"].astype(int)
    df = df.head(n)
    return df[["ticker", "rank"]]


def get_all_stocks() -> List[str]:
    """
    Return all active stocks in the universe.

    Returns:
        List of all active ticker symbols.
    """
    df = _get_stock_daily_data(columns=["ticker"])
    return df["ticker"].unique().tolist()
