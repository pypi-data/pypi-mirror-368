"""
access mkt data
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict, Tuple
import boto3
from botocore.config import Config
from botocore.client import BaseClient
import datetime
import pandas as pd
import os
import json
import hashlib
import time as _time
import threading

from ..utils import time
from ..utils.constants import (
    POLYGON_BASE_URL,
    FMP_BASE_URL,
    PX_RENAME_COLS,
    PAGINATE_LIMIT,
)
from ..utils.logger import get_logger
from ..utils.options import input_to_osi, osi_to_input
from sharpe.utils import env

env.load_env()

# Configure module logger
logger = get_logger(__name__)

### Polygon rest api ###

### general ###


_HTTP_SESSION: requests.Session = None
_HTTP_SESSION_LOCK = threading.Lock()


def _get_http_session() -> requests.Session:
    """Return a module-scoped HTTP session with connection pooling and retries."""
    global _HTTP_SESSION
    if _HTTP_SESSION is not None:
        return _HTTP_SESSION

    with _HTTP_SESSION_LOCK:
        if _HTTP_SESSION is not None:
            return _HTTP_SESSION
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=50, max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _HTTP_SESSION = session
        return _HTTP_SESSION


_MEM_CACHE: dict[str, tuple[float, list]] = {}
_MEM_CACHE_LOCK = threading.Lock()


def _is_cache_enabled() -> bool:
    return os.getenv("SHARPE_HTTP_CACHE_ENABLED", "1") not in ("0", "false", "False")


def _cache_ttl_seconds() -> int:
    try:
        return int(os.getenv("SHARPE_HTTP_CACHE_TTL_SECONDS", "86400"))  # 1 day
    except Exception:
        return 86400


def _cache_dir() -> str:
    base_dir = os.getenv("SHARPE_HTTP_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "sharpe", "http"))
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def _cache_path_for_url(url: str) -> str:
    key = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return os.path.join(_cache_dir(), f"{key}.json")


def _load_from_cache(url: str) -> list | None:
    now = _time.time()
    ttl = _cache_ttl_seconds()

    # In-memory first
    with _MEM_CACHE_LOCK:
        cached = _MEM_CACHE.get(url)
        if cached:
            ts, data = cached
            if now - ts <= ttl:
                return data
            else:
                _MEM_CACHE.pop(url, None)

    # Disk cache
    path = _cache_path_for_url(url)
    if os.path.isfile(path):
        try:
            stat = os.stat(path)
            if now - stat.st_mtime <= ttl:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # populate mem cache
                with _MEM_CACHE_LOCK:
                    _MEM_CACHE[url] = (now, data)
                return data
        except Exception:
            # Ignore cache read errors
            pass
    return None


def _save_to_cache(url: str, data: list) -> None:
    now = _time.time()
    # memory
    with _MEM_CACHE_LOCK:
        _MEM_CACHE[url] = (now, data)
        # simple bound to avoid unbounded growth
        if len(_MEM_CACHE) > 1024:
            # drop oldest ~10%
            for i, k in enumerate(list(_MEM_CACHE.keys())):
                if i % 10 == 0:
                    _MEM_CACHE.pop(k, None)

    # disk
    try:
        path = _cache_path_for_url(url)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        # Ignore disk cache errors
        pass


def _request_url(url: str, timeout: int = 180, paginate: bool = True) -> dict:
    api_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    logger.info(f"Requesting data from {url}")
    try:
        # Try cache first
        if _is_cache_enabled():
            cached = _load_from_cache(url)
            if cached is not None:
                return cached

        session = _get_http_session()
        response = session.get(url, headers=headers, timeout=timeout)

        # Handle 403 Forbidden specifically
        if response.status_code == 403:
            logger.error(f"Forbidden (403) accessing {url}. Continuing anyway.")
            # Return empty results to allow processing to continue
            return []

        if response.status_code != 200:
            logger.error(f"Failed for {url}. Status code: {response.status_code}")
            raise Exception(f"Failed to get data. Status code: {response.status_code}")

        # Parse the JSON response
        json_response = response.json()

        # Check if results are available
        if "results" not in json_response:
            logger.warning(f"No data found. {json_response}")
            return []

        # Get initial results
        all_results = json_response["results"]

        # Handle pagination if enabled and next_url is present
        if paginate and "next_url" in json_response:
            pages_fetched = 1

            # Collect results during pagination
            while "next_url" in json_response:
                try:
                    logger.debug(
                        f"Fetching next page from: {json_response['next_url']}"
                    )
                    response = session.get(
                        json_response["next_url"], headers=headers, timeout=timeout
                    )

                    # Handle 403 in pagination
                    if response.status_code == 403:
                        logger.error(
                            f"Forbidden (403) accessing page {pages_fetched + 1}. Stopping pagination."
                        )
                        break

                    if response.status_code != 200:
                        logger.error(
                            f"Failed to fetch page {pages_fetched + 1}: Status code {response.status_code}"
                        )
                        break

                    json_response = response.json()

                    if "results" not in json_response:
                        logger.error(f"No results found in page {pages_fetched + 1}")
                        break

                    all_results.extend(json_response["results"])
                    pages_fetched += 1

                    if pages_fetched % 5 == 0:
                        logger.info(f"Fetched {pages_fetched} pages of data")

                    # Safety check to prevent infinite loops
                    if pages_fetched >= PAGINATE_LIMIT:
                        logger.warning(
                            f"Reached maximum pagination limit of {PAGINATE_LIMIT} pages"
                        )
                        break

                except Exception as e:
                    logger.error(f"Error fetching page {pages_fetched + 1}: {str(e)}")
                    break

            if pages_fetched > 1:
                logger.info(
                    f"Completed fetching {pages_fetched} pages of data with {len(all_results)} total records"
                )

        # Save to cache
        if _is_cache_enabled():
            _save_to_cache(url, all_results)

        return all_results
    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {timeout} seconds for {url}")
        raise Exception(f"Request timed out after {timeout} seconds")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url}: {str(e)}")
        raise Exception(f"Request failed: {str(e)}")


def _flatten_json(options: list) -> pd.DataFrame:
    res = []
    for option in options:
        flattened = {}
        for key, value in option.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flattened[f"{sub_key}"] = sub_value
            else:
                flattened[key] = value
        res.append(flattened)
    res = pd.DataFrame(res)
    return res


def aggregates(**kwargs: Dict) -> pd.DataFrame:
    """
    aggregate bar data for various intruments

    args:
        kwargs: dict: The query parameters.

        example:
            query = {
                'ticker': 'NVDA',
                'multiplier': 1,
                'timespan': 'day',
                'from': '2024-01-01',
                'to': '2024-06-25'
            }
            options use osi as the ticker

    returns:
        df: pd.DataFrame
        columns include:
            close: float: The close price.
            high: float: The high price.
            low: float: The low price.
            open: float: The open price.
            timestamp: int: The timestamp.
            volume: int: The volume.
            vwap: float: The volume weighted average price.
            num_trades: int: The number of trades.
            datetimes: pd.Timestamp: The timestamp as a datetime object.
            date: str: The date.
            ticker: str: The underlying symbol.
            raw_symbol: str: The raw symbol.
            expiry: str: The expiry.
            flavor: str: The flavor.
            strike: float: The strike.
            freq: str: The frequency.
            secs_open: int: The number of seconds since the market opened.
    """
    url = _aggregate_url(**kwargs)
    df = pd.DataFrame(_request_url(url))

    df = df.rename(columns=PX_RENAME_COLS)

    df["datetimes"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["date"] = df["datetimes"].dt.date

    raw_symbol = kwargs.get("ticker")
    df["ticker"] = (
        osi_to_input(raw_symbol)[0] if raw_symbol.startswith("O:") else raw_symbol
    )
    df["raw_symbol"] = raw_symbol

    df["expiry"] = df.raw_symbol.apply(
        lambda x: osi_to_input(x)[1] if raw_symbol.startswith("O:") else ""
    )
    df["flavor"] = df.raw_symbol.apply(
        lambda x: osi_to_input(x)[2] if raw_symbol.startswith("O:") else ""
    )
    df["strike"] = df.raw_symbol.apply(
        lambda x: osi_to_input(x)[3] if raw_symbol.startswith("O:") else ""
    )
    df["freq"] = f"{kwargs.get('multiplier')}{kwargs.get('timespan')}"

    # Calculate seconds since market open using the first timestamp
    first_timestamp = df["timestamp"].iloc[0]
    seconds_since_first_open = time.seconds_since_mkt_open(first_timestamp)

    # Convert timestamp differences from milliseconds to seconds and add the offset
    df["secs_open"] = ((df["timestamp"] - df["timestamp"].iloc[0]) / 1000).astype(
        int
    ) + seconds_since_first_open

    return df


def _aggregate_url(**kwargs: Dict) -> str:
    """
    generate url endpoint for aggregate bar
    this works for both option and stock

    args:
        ticker: str: The option ticker.
        multiplier: int: The multiplier for the time window.
        timespan: str: The timespan.
        from: str: The start date.
        to: str: The end date.
        adjusted: bool: Whether to adjust the data.
        sort: str: The sort order.
        limit: int: The limit.
        example:
            query = {
                'ticker': 'NVDA',
                'multiplier': 1,
                'timespan': 'day',
                'from': '2024-01-01',
                'to': '2024-06-25'
            }

    returns:
        df: pd.DataFrame: The data.
    """
    ticker = kwargs.get("ticker")
    multiplier = kwargs.get("multiplier")
    timespan = kwargs.get("timespan")
    from_date = kwargs.get("from")
    to_date = kwargs.get("to")
    adjusted = kwargs.get("adjusted", "true")
    sort = kwargs.get("sort", "asc")
    limit = kwargs.get("limit", None)  # FIXME: implement limit

    for time in (from_date, to_date):
        assert (
            len(time) == 13 or len(time) == 10
        ), f"{time} is not a valid timestamp. Must be in milliseconds or %Y-%m-%d format."

    url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}?adjusted={adjusted}&sort={sort}"

    return url


### stock ###


def stock_grouped_daily(date: str) -> pd.DataFrame:
    """
    get stock grouped daily data
    """
    url = f"{POLYGON_BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{date}?unadjusted=false&sort=asc"
    df = pd.DataFrame(_request_url(url))

    if df.empty:
        logger.warning(f"No data found for {date}")
        return df

    df = df.rename(columns=PX_RENAME_COLS)
    df["datetimes"] = df["timestamp"].apply(time.millis_to_datetime)
    df["date"] = df["datetimes"].dt.date
    df["raw_symbol"] = df["ticker"]
    df["num_trades"] = df.num_trades.fillna(0)

    # FIXME: if no vwap, use average of close and open
    df["vwap"] = df.apply(
        lambda x: x["vwap"] if x["vwap"] is None else (x["close"] + x["open"]) / 2,
        axis=1,
    )

    return df


def df_to_stock_grouped_daily(df: pd.DataFrame) -> list:
    """
    Convert DataFrame to StockGroupedDaily objects

    Args:
        df: DataFrame with stock grouped daily data

    Returns:
        list: List of StockGroupedDaily objects
    """
    from .model import StockGroupedDaily

    records = []
    for _, row in df.iterrows():
        record = StockGroupedDaily.create(
            ticker=row["ticker"],
            date=row["date"],
            volume=row["volume"],
            vwap=row["vwap"],
            open=row["open"],
            close=row["close"],
            high=row["high"],
            low=row["low"],
            timestamp=row["timestamp"],
            num_trades=row["num_trades"],
            datetimes=row["datetimes"],
            raw_symbol=row["raw_symbol"],
        )
        records.append(record)
    return records


def related_companies(symbol: str) -> str:
    """
    Get a list of tickers related to the queried ticker based on News and Returns data.
    """
    url = f"{POLYGON_BASE_URL}/v1/related-companies/{symbol}"
    data = _request_url(url)
    tickers = "|".join([row["ticker"] for row in data])

    res = {
        "ticker": symbol,
        "peers": tickers,
        "date": datetime.date.today().strftime("%Y-%m-%d"),
        "source": "polygon",
    }

    return res


def dict_to_related_companies(data: dict) -> "RelatedCompanies":
    """
    Convert dictionary to RelatedCompanies object

    Args:
        data: Dictionary containing related companies data with keys:
            ticker: Stock ticker symbol
            peers: Pipe-separated list of peer tickers
            date: Data date
            source: Data source

    Returns:
        RelatedCompanies object
    """
    from .model import RelatedCompanies

    return RelatedCompanies.create(
        ticker=data["ticker"],
        date=datetime.datetime.strptime(data["date"], "%Y-%m-%d").date(),
        source=data["source"],
        peers=data["peers"],
    )


### option ###


def options_chain(
    ticker: str, downsample_query: str = "volume > 1000 or open_interest > 1000"
) -> pd.DataFrame:
    """
    given a ticker and date, get all the available options

    args:
        ticker: str: The option ticker.

    returns:
        df: pd.DataFrame: ticker | expiry | strike | flavor | volume | oi | greeks
    """
    date = time.closest_trading_day(datetime.date.today())
    api_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    end_date = time.closest_trading_day(
        datetime.date.today() + datetime.timedelta(days=60)
    )  # next 2 months only

    # Get first page
    url = f"{POLYGON_BASE_URL}/v3/snapshot/options/{ticker}?strike_price.gte=0&limit={PAGINATE_LIMIT}&expiration_date.gte={date}&expiration_date.lte={end_date}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to get data. Status code: {response.status_code}")

    json_response = response.json()
    all_results = json_response.get("results", [])

    # If no results in first page, return empty DataFrame with correct columns
    if not all_results:
        return pd.DataFrame(
            columns=[
                "ticker",
                "strike_price",
                "expiration_date",
                "contract_type",
                "volume",
                "open_interest",
                "osi",
                "date",
            ]
        )

    pages_fetched = 1

    # Collect results during pagination
    while "next_url" in json_response:
        try:
            response = requests.get(json_response["next_url"], headers=headers)
            json_response = response.json()
            all_results.extend(json_response["results"])
            pages_fetched += 1
            if pages_fetched % 5 == 0:
                logger.info(f"Fetched {pages_fetched} pages of options data")
        except Exception as e:
            logger.error(f"Error fetching page {pages_fetched}: {str(e)}")
            break

    logger.info(f"Completed fetching {pages_fetched} pages of options data")
    options = _flatten_json(all_results)

    if downsample_query:
        options = options.query(downsample_query).copy()

    # Generate OSI and add date
    options["osi"] = options.apply(
        lambda x: input_to_osi(
            x.ticker, x.contract_type, x.expiration_date, x.strike_price
        ),
        axis=1,
    )
    options["date"] = pd.to_datetime(date).date()
    options["expiration_date"] = pd.to_datetime(options["expiration_date"]).dt.date

    options[["volume", "open_interest"]] = options[["volume", "open_interest"]].fillna(
        0
    )

    return options


def df_to_options_chain_snapshot(df: pd.DataFrame) -> list:
    """
    Convert DataFrame to OptionsChainSnapshot objects

    Args:
        df: DataFrame with options chain data

    Returns:
        list: List of OptionsChainSnapshot objects
    """
    from .model import OptionsChainSnapshot

    logger.debug(f"Converting DataFrame with columns: {df.columns}")

    records = []
    for idx, row in df.iterrows():
        try:
            record = OptionsChainSnapshot.create(
                osi=row["osi"],
                date=row["date"],  # Use date as part of unique key
                ticker=row["ticker"],
                last_updated=row["last_updated"],  # Keep last_updated as regular field
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                previous_close=row["previous_close"],
                change=row["change"],
                change_percent=row["change_percent"],
                volume=row["volume"],
                vwap=row["vwap"],
                strike_price=row["strike_price"],
                expiration_date=row["expiration_date"],  # Already a date object
                contract_type=row["contract_type"].lower(),
                open_interest=row["open_interest"],
                delta=row["delta"],
                gamma=row["gamma"],
                theta=row["theta"],
                vega=row["vega"],
                implied_volatility=row["implied_volatility"],
            )

            records.append(record)
            logger.debug(f"Successfully converted record {idx} for {row['ticker']}")
        except Exception as e:
            logger.error(f"Error converting record {idx} for {row['ticker']}: {e}")
            logger.error(f"Row data: {row.to_dict()}")
            raise

    return records


def option_definition(
    underlying_ticker: str = None,
    contract_type: str = None,
    expiration_date: str = None,
    expiration_date_gte: str = None,
    expiration_date_gt: str = None,
    expiration_date_lte: str = None,
    expiration_date_lt: str = None,
    strike_price: float = None,
    strike_price_gte: float = None,
    strike_price_gt: float = None,
    strike_price_lte: float = None,
    strike_price_lt: float = None,
    as_of: str = None,
    expired: bool = False,
    order: str = "asc",
    limit: int = 10,
    sort: str = "ticker",
    paginate: bool = True,
) -> pd.DataFrame:
    """
    Retrieve a comprehensive index of options contracts, encompassing both active and expired listings.

    Args:
        underlying_ticker: Query for contracts relating to an underlying stock ticker (e.g. "SPY")
        contract_type: Query by the type of contract ("call" or "put")
        expiration_date: Query by contract expiration with date format YYYY-MM-DD
        expiration_date_gte: Search expiration_date >= given value (YYYY-MM-DD)
        expiration_date_gt: Search expiration_date > given value (YYYY-MM-DD)
        expiration_date_lte: Search expiration_date <= given value (YYYY-MM-DD)
        expiration_date_lt: Search expiration_date < given value (YYYY-MM-DD)
        strike_price: Query by exact strike price of a contract
        strike_price_gte: Search strike_price >= given value
        strike_price_gt: Search strike_price > given value
        strike_price_lte: Search strike_price <= given value
        strike_price_lt: Search strike_price < given value
        as_of: Specify a point in time for contracts as of this date (YYYY-MM-DD, defaults to today)
        expired: Query for expired contracts (default is False)
        order: Order results based on the sort field ("asc" or "desc", default "asc")
        limit: Limit the number of results returned (default 10, max 1000)
        sort: Sort field used for ordering (default "ticker")
        paginate: Whether to fetch all pages (default True)

    Returns:
        pd.DataFrame: Options contracts data with columns including:
            - ticker: Option contract ticker (OSI format)
            - underlying_ticker: Underlying stock ticker
            - contract_type: "call" or "put"
            - exercise_style: Exercise style (e.g., "american")
            - expiration_date: Contract expiration date
            - strike_price: Strike price
            - shares_per_contract: Number of shares per contract
            - primary_exchange: Primary exchange
            - cfi: Classification of Financial Instruments code

    Raises:
        Exception: If API call fails or no data found

    Example:
        >>> # Get all SPY call options expiring on or after 2025-01-10
        >>> contracts = option_definition(
        ...     underlying_ticker="SPY",
        ...     contract_type="call",
        ...     expiration_date_gte="2025-01-10",
        ...     limit=100
        ... )
        >>> print(contracts[['ticker', 'strike_price', 'expiration_date']])
    """
    # Build query parameters
    params = []

    if underlying_ticker:
        params.append(f"underlying_ticker={underlying_ticker}")
    if contract_type:
        params.append(f"contract_type={contract_type.lower()}")
    if expiration_date:
        params.append(f"expiration_date={expiration_date}")
    if expiration_date_gte:
        params.append(f"expiration_date.gte={expiration_date_gte}")
    if expiration_date_gt:
        params.append(f"expiration_date.gt={expiration_date_gt}")
    if expiration_date_lte:
        params.append(f"expiration_date.lte={expiration_date_lte}")
    if expiration_date_lt:
        params.append(f"expiration_date.lt={expiration_date_lt}")
    if strike_price is not None:
        params.append(f"strike_price={strike_price}")
    if strike_price_gte is not None:
        params.append(f"strike_price.gte={strike_price_gte}")
    if strike_price_gt is not None:
        params.append(f"strike_price.gt={strike_price_gt}")
    if strike_price_lte is not None:
        params.append(f"strike_price.lte={strike_price_lte}")
    if strike_price_lt is not None:
        params.append(f"strike_price.lt={strike_price_lt}")
    if as_of:
        params.append(f"as_of={as_of}")
    if expired:
        params.append(f"expired={str(expired).lower()}")

    params.extend([f"order={order}", f"limit={limit}", f"sort={sort}"])

    # Build URL
    query_string = "&".join(params)
    url = f"{POLYGON_BASE_URL}/v3/reference/options/contracts?{query_string}"

    # Make API call
    results = _request_url(url, paginate=paginate)

    if not results:
        logger.warning("No options contracts found matching the criteria")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Convert expiration_date to datetime
    if "expiration_date" in df.columns:
        df["expiration_date"] = pd.to_datetime(df["expiration_date"]).dt.date

    logger.info(f"Retrieved {len(df)} options contracts")

    return df


def treasury_yield(date: str) -> pd.DataFrame:
    """
    Get treasury yield data for a single date

    Args:
        date: Date in YYYY-MM-DD format

    Returns:
        pd.DataFrame: Treasury yield data with columns:
            date | month1 | month2 | month3 | month6 | year1 | year2 | year3 | year5 | year7 | year10 | year20 | year30

    Example:
        >>> treasury_yield("2024-01-01")
    """
    url = f"{FMP_BASE_URL}/v4/treasury?from={date}&to={date}"
    api_key = os.getenv("FMP_ACCESS_KEY")
    params = {
        "apikey": api_key,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching treasury yield data: {response.status_code}")

    data = response.json()
    df = pd.DataFrame(data)

    return df


def df_to_treasury_yield(df: pd.DataFrame) -> list:
    """
    Convert DataFrame to TreasuryYield objects

    Args:
        df: DataFrame with treasury yield data

    Returns:
        list: List of TreasuryYield objects

    Raises:
        KeyError: If any required yield data is missing
    """
    from .model import TreasuryYield

    logger.debug(f"Converting DataFrame with columns: {df.columns}")

    records = []
    for idx, row in df.iterrows():
        try:
            record = TreasuryYield.create(
                date=pd.to_datetime(row["date"]).date(),
                month1=float(row["month1"]),
                month2=float(row["month2"]),
                month3=float(row["month3"]),
                month6=float(row["month6"]),
                year1=float(row["year1"]),
                year2=float(row["year2"]),
                year3=float(row["year3"]),
                year5=float(row["year5"]),
                year7=float(row["year7"]),
                year10=float(row["year10"]),
                year20=float(row["year20"]),
                year30=float(row["year30"]),
            )
            records.append(record)
            logger.debug(f"Successfully converted record {idx} for {row['date']}")
        except Exception as e:
            logger.error(f"Error converting record {idx} for {row['date']}: {e}")
            logger.error(f"Row data: {row.to_dict()}")
            raise

    return records


### S3 ###


def session() -> BaseClient:
    """
    returns: Any: A boto3 session object.
    """

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    s3 = session.client(
        "s3",
        endpoint_url="https://files.polygon.io",
        config=Config(signature_version="s3v4"),
    )

    return s3


def download_file(prefix: str, local_dir: str, date: str) -> None:
    """
    args:
        prefix: str: The prefix of the files to download.
        local_dir: str: The local directory to download the files to.
        date: str: The date of the files to download.
    """
    s3 = session()
    date_dt = datetime.datetime.strptime(date, "%Y%m%d")
    object_key = (
        f"{prefix}/trades_v1/{date_dt:%Y}/{date_dt:%m}/{date_dt:%Y-%m-%d}.csv.gz"
    )

    assert os.path.isdir(local_dir), f"{local_dir} is not a directory."
    local_file_name = os.path.join(prefix, object_key.split("/")[-1])
    local_file_path = os.path.join(local_dir, local_file_name)

    s3.download_file("flatfiles", object_key, local_file_path)


def show_file(prefix: str) -> None:
    """
    args:
        prefix: str: The prefix of the files to download.
    """
    s3 = session()
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket="flatfiles", Prefix=prefix):
        for obj in page["Contents"]:
            print(obj["Key"])
