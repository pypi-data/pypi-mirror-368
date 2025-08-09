"""
Trading-related utility functions
"""

import pandas as pd
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm
import math
import datetime
import re
from typing import Dict, Any, Tuple, List
from .constants import DELTA_BUCKET_RANGES
from ..utils.logger import get_logger
from ..utils import time

# Configure module logger
logger = get_logger(__name__)


def get_delta_bucket(delta: float) -> str:
    """Get the delta bucket for a given delta value based on predefined ranges

    Args:
        delta: Option delta value

    Returns:
        String representing the delta bucket range
    """
    if pd.isna(delta):
        return "N/A"

    abs_delta = abs(delta)

    # Handle edge case of delta = 0
    if abs_delta == 0:
        return "0"

    # Find the appropriate bucket
    for i in range(len(DELTA_BUCKET_RANGES) - 1):
        if abs_delta <= DELTA_BUCKET_RANGES[i + 1]:
            return f"{DELTA_BUCKET_RANGES[i]}-{DELTA_BUCKET_RANGES[i + 1]}"

    return f"{DELTA_BUCKET_RANGES[-2]}-{DELTA_BUCKET_RANGES[-1]}"


def implied_volatility_from_straddle(
    underlying_price: float,
    straddle_px: float,
    dte: int,
    strike: float = None,
    risk_free_rate: float = 0.05,
) -> float:
    """
    Solve for implied volatility given underlying price, straddle price, and days to expiration

    Args:
        underlying_price: Current price of underlying asset
        straddle_px: Market price of the straddle (call + put)
        dte: Days to expiration
        strike: Strike price (defaults to underlying_price for ATM)
        risk_free_rate: Risk-free rate (defaults to 5%)

    Returns:
        Implied volatility (annualized)

    Raises:
        ValueError: If unable to solve for implied volatility

    Example:
        >>> implied_volatility_from_straddle(100.0, 8.50, 30)
        0.2543  # 25.43% annualized volatility
    """
    # Default to ATM strike if not provided
    if strike is None:
        strike = underlying_price

    # Convert days to years
    T = dte / 252.0

    # Handle edge case of zero time to expiration
    if T <= 0:
        intrinsic_value = abs(underlying_price - strike)
        if straddle_px <= intrinsic_value:
            return 0.0
        else:
            raise ValueError("Straddle price exceeds intrinsic value at expiration")

    def black_scholes_call(S, K, T, r, sigma):
        if T <= 0:
            return max(S - K, 0)
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

    def black_scholes_put(S, K, T, r, sigma):
        if T <= 0:
            return max(K - S, 0)
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    def straddle_price(S, K, T, r, sigma):
        return black_scholes_call(S, K, T, r, sigma) + black_scholes_put(
            S, K, T, r, sigma
        )

    # Define objective function: difference between theoretical and market straddle price
    def objective(sigma: float) -> float:
        theoretical_price = straddle_price(
            underlying_price, strike, T, risk_free_rate, sigma
        )
        return theoretical_price - straddle_px

    try:
        # Use Brent's method to find the root (volatility that makes objective = 0)
        # Search between 1% and 500% volatility
        implied_vol = brentq(objective, 0.01, 5.0, xtol=1e-6)
        return implied_vol

    except ValueError as e:
        # If root finding fails, try to provide helpful error message
        low_vol_price = straddle_price(
            underlying_price, strike, T, risk_free_rate, 0.01
        )
        high_vol_price = straddle_price(
            underlying_price, strike, T, risk_free_rate, 5.0
        )

        raise ValueError(
            f"Unable to solve for implied volatility. "
            f"Market straddle price: {straddle_px:.2f}, "
            f"Theoretical range: {low_vol_price:.2f} - {high_vol_price:.2f}"
        ) from e


def find_strike_by_delta(
    underlying_price: float,
    target_delta: float,
    dte: int,
    implied_vol: float,
    option_type: str = "call",
    risk_free_rate: float = 0.05,
) -> float:
    """
    Find the strike price that gives a target delta for an option

    Args:
        underlying_price: Current price of underlying asset
        target_delta: Target delta value (e.g., 0.5 for 50 delta)
        dte: Days to expiration
        implied_vol: Implied volatility (annualized)
        option_type: "call" or "put"
        risk_free_rate: Risk-free rate (defaults to 5%)

    Returns:
        Strike price that produces the target delta

    Raises:
        ValueError: If unable to solve for strike or invalid inputs

    Example:
        >>> find_strike_by_delta(100.0, 0.5, 30, 0.25, "call")
        100.42  # Strike price for 50 delta call
    """
    if not -1.0 <= target_delta <= 1.0:
        raise ValueError("Target delta must be between -1.0 and 1.0")

    if option_type.lower() not in ["call", "put"]:
        raise ValueError("Option type must be 'call' or 'put'")

    if dte < 0:
        raise ValueError("Days to expiration cannot be negative")

    if implied_vol <= 0:
        raise ValueError("Implied volatility must be positive")

    # Add 1 to DTE since calculations are typically done at market open
    # but options don't expire until market close
    effective_dte = dte + 1

    # Convert days to years
    T = effective_dte / 252.0

    def calculate_delta(strike: float) -> float:
        """Calculate option delta for given strike"""
        if strike <= 0:
            return float("inf") if option_type.lower() == "put" else float("-inf")

        d1 = (
            math.log(underlying_price / strike)
            + (risk_free_rate + 0.5 * implied_vol**2) * T
        ) / (implied_vol * math.sqrt(T))

        if option_type.lower() == "call":
            return norm.cdf(d1)
        else:  # put
            return norm.cdf(d1) - 1.0

    # Define objective function: difference between calculated and target delta
    def objective(strike: float) -> float:
        calculated_delta = calculate_delta(strike)
        return calculated_delta - target_delta

    # Set search bounds based on option type and underlying price
    if option_type.lower() == "call":
        # For calls, search from very low strike (high delta) to high strike (low delta)
        lower_bound = underlying_price * 0.1  # Very ITM
        upper_bound = underlying_price * 3.0  # Very OTM
    else:  # put
        # For puts, search from low strike (low delta) to high strike (high delta)
        lower_bound = underlying_price * 0.1  # Very OTM
        upper_bound = underlying_price * 3.0  # Very ITM

    try:
        # Use Brent's method to find the strike that gives target delta
        target_strike = brentq(objective, lower_bound, upper_bound, xtol=1e-6)
        return round(target_strike, 2)  # Round to nearest cent

    except ValueError as e:
        # If root finding fails, provide helpful error message
        low_delta = calculate_delta(lower_bound)
        high_delta = calculate_delta(upper_bound)

        raise ValueError(
            f"Unable to find strike for target delta {target_delta:.2f}. "
            f"Delta range available: {min(low_delta, high_delta):.2f} to {max(low_delta, high_delta):.2f} "
            f"for {option_type} with {dte} DTE and {implied_vol:.1%} IV"
        ) from e


def find_closest_option_strike(
    ticker: str,
    expiry_date: str,
    target_price: float,
    as_of_date: str,
    option_type: str = "call",
) -> str:
    """
    Find the actual market option with strike closest to a target price

    Args:
        ticker: Underlying ticker symbol
        expiry_date: Option expiration date in YYYY-MM-DD format
        target_price: Target strike price to find closest match for
        as_of_date: Optional reference date (defaults to today)
        option_type: "call" or "put"


    Returns:
        OSI symbol of the option with closest strike

    Raises:
        Exception: If no options found or API call fails

    Example:
        >>> find_closest_option_strike("SPY", "2025-01-10", 582.50, "call")
        "O:SPY250110C00583000"
    """
    # Use helper function to find options around target price
    options_results = find_options_around_price(
        ticker=ticker,
        expiry_date=expiry_date,
        target_price=target_price,
        as_of_date=as_of_date,
        option_type=option_type,
        search_ranges=[max(5, target_price * 0.01), max(10, target_price * 0.05)],
        limit=10,
    )

    # Find the option with strike closest to target price
    closest_option = None
    min_diff = float("inf")

    for option in options_results:
        strike = option["strike_price"]
        diff = abs(strike - target_price)
        if diff < min_diff:
            min_diff = diff
            closest_option = option

    if closest_option is None:
        raise Exception(f"Could not find suitable {option_type} option for {ticker}")

    # Generate OSI symbol for the closest option
    closest_strike = closest_option["strike_price"]
    osi = input_to_osi(ticker, option_type.lower(), expiry_date, closest_strike)

    return osi


def get_atm_straddle_price(
    ticker: str, expiry_date: str, as_of_date: str = None
) -> Dict[str, Any]:
    """
    Get the straddle price for at-the-money options (call + put at same strike)

    Args:
        ticker: The underlying ticker symbol
        expiry_date: Option expiration date in YYYY-MM-DD format
        as_of_date: Optional reference date in YYYY-MM-DD format (defaults to today)

    Returns:
        Dict containing:
            - ticker: str
            - expiry_date: str
            - atm_strike: float (strike price closest to underlying price)
            - underlying_price: float (current stock price)
            - call_price: float (mid price of call option)
            - put_price: float (mid price of put option)
            - straddle_price: float (call_price + put_price)
            - call_osi: str (call option OSI symbol)
            - put_osi: str (put option OSI symbol)

    Raises:
        Exception: If no options are found or API call fails

    Example:
        >>> get_atm_straddle_price("SPY", "2025-01-10")
        {
            "ticker": "SPY",
            "expiry_date": "2025-01-10",
            "atm_strike": 580.0,
            "underlying_price": 580.50,
            "call_price": 5.25,
            "put_price": 4.75,
            "straddle_price": 10.00,
            "call_osi": "O:SPY250110C00580000",
            "put_osi": "O:SPY250110P00580000"
        }
    """
    # Import here to avoid circular imports
    from sharpe.data.mkt import aggregates

    if as_of_date is None:
        as_of_date = datetime.date.today().strftime("%Y-%m-%d")

    logger.info(f"Getting ATM straddle for {ticker} expiring {expiry_date}")

    # Get underlying stock price for the as_of_date
    stock_query = {
        "ticker": ticker,
        "multiplier": 1,
        "timespan": "day",
        "from": as_of_date,
        "to": as_of_date,
    }
    stock_df = aggregates(**stock_query)

    if stock_df.empty:
        raise Exception(f"No stock data found for {ticker} on {as_of_date}")

    underlying_price = stock_df["open"].iloc[0]
    logger.info(f"{ticker} price on {as_of_date}: ${underlying_price}")

    search_ranges = [
        max(1, underlying_price * 0.01),
        max(5, underlying_price * 0.05),
    ]   
    # Use helper function to find call options with progressive search ranges
    call_results = find_options_around_price(
        ticker=ticker,
        expiry_date=expiry_date,
        target_price=underlying_price,
        as_of_date=as_of_date,
        option_type="call",
        search_ranges=search_ranges,
        limit=10,
    )

    # Find the strike price closest to underlying price
    closest_strike = None
    min_diff = float("inf")

    for option in call_results:
        strike = option["strike_price"]
        diff = abs(strike - underlying_price)
        if diff < min_diff:
            min_diff = diff
            closest_strike = strike

    if closest_strike is None:
        raise Exception(f"Could not find suitable strike price for {ticker}")

    logger.info(
        f"Found ATM strike: ${closest_strike} (underlying: ${underlying_price})"
    )

    # Helper function to safely get option data
    def get_option_data(osi: str, option_type: str) -> float:
        """
        Safely get option data with fallback mechanism

        Args:
            osi: Option OSI symbol
            option_type: "call" or "put"

        Returns:
            Option price (open price)

        Raises:
            Exception: If no tradeable option data can be found
        """
        query = {
            "ticker": osi,
            "multiplier": 1,
            "timespan": "day",
            "from": as_of_date,
            "to": as_of_date,
        }

        try:
            df = aggregates(**query)
            if not df.empty:
                return df["open"].iloc[0]
            else:
                logger.warning(f"No trading data found for {osi} on {as_of_date}")
                return None
        except Exception as e:
            logger.warning(f"Failed to get data for {osi} on {as_of_date}: {e}")
            return None

    # Try to find tradeable options, starting with ATM strike
    available_strikes = sorted([option["strike_price"] for option in call_results])

    # Sort strikes by distance from ATM strike
    sorted_strikes = sorted(available_strikes, key=lambda x: abs(x - closest_strike))

    call_price = None
    put_price = None
    final_strike = None
    call_osi = None
    put_osi = None

    # Try each strike until we find one with both call and put data
    for strike in sorted_strikes:
        logger.info(f"Trying strike ${strike}")

        # Generate OSI symbols for this strike
        test_call_osi = input_to_osi(ticker, "call", expiry_date, strike)
        test_put_osi = input_to_osi(ticker, "put", expiry_date, strike)

        # Try to get call and put data
        test_call_price = get_option_data(test_call_osi, "call")
        test_put_price = get_option_data(test_put_osi, "put")

        if test_call_price is not None and test_put_price is not None:
            # Found tradeable options at this strike
            call_price = test_call_price
            put_price = test_put_price
            final_strike = strike
            call_osi = test_call_osi
            put_osi = test_put_osi
            logger.info(f"Successfully found tradeable options at strike ${strike}")
            break
        else:
            logger.info(
                f"No tradeable straddle data for strike ${strike}, trying next closest strike"
            )

    if call_price is None or put_price is None:
        raise Exception(
            f"No tradeable straddle found for {ticker} expiring {expiry_date} on {as_of_date}"
        )

    # Sanity check: Call and put prices should be within 50% of each other for ATM straddles
    price_ratio = max(call_price, put_price) / min(call_price, put_price)
    assert price_ratio <= 5.0 or call_price + put_price < 3.0, (
        f"Call and put prices are too different for ATM straddle: "
        f"Call=${call_price:.2f}, Put=${put_price:.2f}, Ratio={price_ratio:.2f}x. "
        f"Expected ratio <= 5.0x for strike ${final_strike}"
    )

    straddle_price = call_price + put_price

    # Calculate implied volatility from straddle price
    dte = time.count_trading_days(as_of_date, expiry_date)

    try:
        implied_vol = implied_volatility_from_straddle(
            underlying_price=underlying_price,
            straddle_px=straddle_price,
            dte=dte,
            strike=final_strike,
        )
    except ValueError as e:
        logger.warning(f"Could not calculate implied volatility: {e}")
        implied_vol = None

    result = {
        "ticker": ticker,
        "expiry_date": expiry_date,
        "atm_strike": final_strike,  # This might be different from closest_strike if we had to use a fallback
        "underlying_price": underlying_price,
        "call_price": call_price,
        "put_price": put_price,
        "straddle_price": straddle_price,
        "call_osi": call_osi,
        "put_osi": put_osi,
        "as_of_date": as_of_date,
        "dte": dte,
        "implied_volatility": implied_vol,
    }

    logger.info(
        f"ATM straddle price for {ticker}: ${straddle_price:.2f} (C: ${call_price:.2f}, P: ${put_price:.2f}) at strike ${final_strike}"
    )

    return result


def input_to_osi(symbol: str, flavor: str, expiry: str, strike: float) -> str:
    """
    get option ticker string

    args:
        symbol: str: The symbol of the option.
        flavor: str: The flavor of the option.
        expiry: str: The expiry of the option.
        strike: float: The strike of the option.
    """
    if flavor.lower() in ["call", "c"]:
        flavor = "C"
    elif flavor.lower() in ["put", "p"]:
        flavor = "P"
    else:
        raise ValueError("Invalid option flavor")

    symbol_str = ""
    symbol_str += "O:"
    symbol_str += symbol
    symbol_str += datetime.datetime.strptime(expiry, "%Y-%m-%d").strftime("%y%m%d")
    symbol_str += flavor

    strike_num = str(int(strike * 1000))
    MAX_OPTION_STRIKE_LEN = (
        8  # FIXME: how does this work if the strike is above 99,999 (e.g. BRK.B)
    )
    prefix_num = "".join(
        ["0" for i in range(MAX_OPTION_STRIKE_LEN - len(str(strike_num)))]
    )
    strike_num = prefix_num + strike_num
    symbol_str += strike_num

    return symbol_str


def osi_to_input(osi: str) -> Tuple[str, str, str, float]:
    """
    get symbol / date / flavor / strike from osi

    args:
        osi: str: The OSI symbol (e.g. "O:TSLA240119C00250000")

    returns:
        Tuple[str, str, str, float]: (symbol, date, flavor, strike)

    raises:
        ValueError: If the OSI format is invalid
    """
    if not osi.startswith("O:"):
        raise ValueError("Invalid OSI format: must start with 'O:'")

    osi = osi.split(":")[1]

    match = re.match(r"([A-Za-z]+)(\d{6})([CP])(\d+)", osi)
    if not match:
        raise ValueError(
            "Invalid OSI format: must match pattern SYMBOL+YYMMDD+[CP]+STRIKE"
        )

    symbol, date, c_or_p, strike = match.groups()

    if c_or_p not in ["C", "P"]:
        raise ValueError("Invalid option flavor: must be 'C' or 'P'")

    # Convert date to more readable format
    try:
        date = f"20{date[:2]}-{date[2:4]}-{date[4:6]}"
        # Validate date format
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format in OSI: {e}")

    # Convert strike price to a readable format
    try:
        strike = (
            int(strike) / 1000
        )  # Assuming the strike price needs to be divided by 1000
    except ValueError:
        raise ValueError("Invalid strike price format in OSI")

    return symbol, date, c_or_p, strike


def closest_option_expiry(ticker: str, as_of_date: str, days_from_as_of: int) -> str:
    """
    Get the closest option expiry date for a given ticker

    Args:
        ticker: The underlying ticker symbol
        as_of_date: Reference date in YYYY-MM-DD format
        days_from_as_of: Minimum number of days from as_of_date to look for expiries

    Returns:
        str: The closest expiry date in YYYY-MM-DD format

    Raises:
        Exception: If no expiry dates are found or API call fails

    Example:
        >>> closest_option_expiry("SPY", "2025-01-02", 7)
        "2025-01-10"
    """
    # Import here to avoid circular imports
    from sharpe.data.mkt import option_definition

    # Calculate minimum expiration date
    min_expiry_date = time.next_trading_day(as_of_date, days_from_as_of)

    logger.info(f"Finding closest option expiry for {ticker} after {min_expiry_date}")

    # Use option_definition to get available contracts
    try:
        contracts_df = option_definition(
            underlying_ticker=ticker,
            contract_type="call",  # Use call since expiries are the same for both
            expiration_date_gte=min_expiry_date,
            as_of=as_of_date,
            order="asc",
            sort="expiration_date",
            limit=5,  # Get multiple expiries to find the closest
            paginate=False,
        )
    except Exception as e:
        raise Exception(f"Failed to fetch option contracts for {ticker}: {e}")

    if contracts_df.empty:
        raise Exception(
            f"No option contracts found for {ticker} with expiry >= {min_expiry_date}"
        )

    # Extract unique expiry dates and find the closest
    expiry_dates = contracts_df["expiration_date"].unique().tolist()

    if not expiry_dates:
        raise Exception(f"No expiry dates found for {ticker}")

    # Since results are sorted by expiration_date ascending, first expiry is closest
    closest_expiry = sorted(expiry_dates)[0]

    logger.info(f"Found closest expiry: {closest_expiry} for {ticker}")
    return datetime.datetime.strftime(closest_expiry, "%Y-%m-%d")


def find_options_around_price(
    ticker: str,
    expiry_date: str,
    target_price: float,
    as_of_date: str,
    option_type: str = "call",
    search_ranges: List[float] = None,
    limit: int = 10,
) -> List[Dict]:
    """
    Find options around a target price using option_definition API

    Args:
        ticker: Underlying ticker symbol
        expiry_date: Option expiration date in YYYY-MM-DD format
        target_price: Target price to search around
        as_of_date: Reference date in YYYY-MM-DD format
        option_type: "call" or "put"
        search_ranges: List of dollar amounts to search around target price (e.g., [5, 10, 50])
                      If None, uses [10] for single range search (+/-$10)
        limit: Maximum number of options to return

    Returns:
        List of option contracts as dictionaries

    Raises:
        Exception: If no options found or API call fails

    Example:
        >>> find_options_around_price("SPY", "2025-01-10", 580.0, "2025-01-02", search_ranges=[5, 10])
        [{"strike_price": 575.0, ...}, {"strike_price": 580.0, ...}]
    """
    # Import here to avoid circular imports
    from sharpe.data.mkt import option_definition

    if option_type.lower() not in ["call", "put"]:
        raise ValueError("Option type must be 'call' or 'put'")

    # Default search ranges if not provided
    if search_ranges is None:
        search_ranges = [10]  # Default to +/-$10 range

    logger.info(
        f"Searching for {option_type} options around ${target_price} for {ticker}"
    )

    options_results = None

    # Try each search range until we find options
    for dollar_range in search_ranges:
        lower_bound = math.floor(target_price - dollar_range)
        upper_bound = math.ceil(target_price + dollar_range)

        logger.info(
            f"Searching for {option_type} options with strikes between ${lower_bound} and ${upper_bound} (+/-${dollar_range})"
        )

        try:
            # Use option_definition instead of manual URL construction
            contracts_df = option_definition(
                underlying_ticker=ticker,
                contract_type=option_type.lower(),
                expiration_date=expiry_date,
                strike_price_gte=lower_bound,
                strike_price_lte=upper_bound,
                as_of=as_of_date,
                order="asc",
                sort="strike_price",
                limit=limit,
                paginate=False,
            )

            if not contracts_df.empty:
                # Convert DataFrame to list of dictionaries for compatibility
                options_results = contracts_df.to_dict("records")
                logger.info(
                    f"Found {len(options_results)} {option_type} options in +/-${dollar_range} range"
                )
                break
            else:
                logger.info(
                    f"No {option_type} options found in +/-${dollar_range} range"
                )

        except Exception as e:
            logger.warning(
                f"Failed to search {option_type} options in +/-${dollar_range} range: {e}"
            )
            continue

    if not options_results:
        ranges_str = ", ".join([f"+/-${r}" for r in search_ranges])
        raise Exception(
            f"No {option_type} options found for {ticker} expiring {expiry_date} "
            f"around ${target_price} with search ranges: {ranges_str}"
        )

    return options_results
