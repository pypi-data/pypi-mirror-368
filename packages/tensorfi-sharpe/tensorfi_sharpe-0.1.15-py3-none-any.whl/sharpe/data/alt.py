"""
fetch and process alternative data sources, such as news, press releases, earnings transcripts, company profiles, and share floats.
"""

import os
import datetime
import pandas as pd
import yaml
import asyncio
import aiohttp
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import re
from typing import Iterable, Dict, List, Union
import time

from .model import (
    ArticleContent,
    ArticleTickerMap,
    PressRelease,
    EarningsTranscript,
    CompanyProfile,
    CompanyShareFloat,
    PriceTarget,
    AnalystRatingChange,
    EarningsCalendar,
    EconomicsCalendar,
    EconomicIndicator,
)
from ..utils.constants import FMP_BASE_URL
from ..utils.logger import get_logger
import logging

from sharpe.utils import env

env.load_env()

# Configure module logger
logger = get_logger(__name__)

PAGINATE_LIMIT = 250
LENGTH_LIMIT = 5000
PAGE_COUNT_LIMIT = 5
MAX_ARTICLE_COUNT_PER_DAY = 100
MAX_CONCURRENT_REQUESTS = 20

### api ###


def news(ticker: str, **kwargs) -> Iterable[ArticleContent]:
    """
    get news for a given company from predefined sources

    args:
        ticker: str: The ticker.
        **kwargs:
            start_date: str: The start date.
            end_date: str: The end date.
            sources: list: The sources to use.
    """
    source_mapping = {
        "polygon_ticker_news": polygon_ticker_news,
        "fmp_stock_news": fmp_stock_news,
    }
    results = []
    sources = kwargs.get("sources") or source_mapping.keys()

    for source in sources:
        if source not in source_mapping:
            raise ValueError(f"Unknown source: {source}")
        try:
            results += source_mapping[source](
                ticker, kwargs.get("start_date"), kwargs.get("end_date")
            )
        except Exception as e:
            logger.error(f"Error processing {source}: {e}")
            continue

    return results


### Polygon ###


def polygon_ticker_news(
    ticker: str, start_date: str, end_date: str
) -> Iterable[tuple[ArticleContent, ArticleTickerMap]]:
    """
    get news for a given ticker

    args:
        ticker: str: The ticker.
        start_date: datetime: The start date.
        end_date: datetime: The end date.

    returns:
        list of tuples, each containing (ArticleContent, ArticleTickerMap)
    """
    articles = _polygon_ticker_news(ticker, start_date, end_date)
    results = []

    # Collect URLs first
    valid_articles = []
    urls = []
    for article in articles:
        valid_articles.append(article)
        urls.append(article["article_url"])

    # Fetch all articles in parallel
    texts = _get_articles(urls)

    # Process articles with their content
    for article, text in zip(valid_articles, texts):
        if not text:
            continue

        text = _process_text(text)
        is_relevant, reason = _is_relevant(text, article["title"], ticker)

        if is_relevant:
            # Create the article content first
            article_content = ArticleContent.create(
                url=article.get("article_url", ""),
                title=article.get("title", ""),
                news_source=article.get("name", ""),
                author=article.get("author", ""),
                description=article.get("description", ""),
                published_time=datetime.datetime.strptime(
                    article["published_utc"], "%Y-%m-%dT%H:%M:%SZ"
                ),
                date=datetime.datetime.strptime(
                    article["published_utc"], "%Y-%m-%dT%H:%M:%SZ"
                ).date(),
                content=text,
                word_length=len(text.split()),
                char_length=len(text),
                api="polygon_ticker_news",
            )

            # Create the ticker mapping
            article_ticker_map = ArticleTickerMap.create(
                article_id=article_content.id,
                ticker=ticker,
            )

            # Add both to results
            results.append((article_content, article_ticker_map))

    return results


def _polygon_ticker_news(ticker: str, start_date: str, end_date: str) -> Iterable:
    """
        get news for a given ticker

        args:
            ticker: str: The ticker.
            start_date: str. %Y-%m-%d
            end_date: str. %Y-%m-%d
    å
        returns:
            df: pd.DataFrame: The news.
    """
    limit = 10

    url = (
        f"https://api.polygon.io/v2/reference/news?"
        + f"ticker={ticker}"
        + f"&limit={limit}"
        + "&order=descending"
        + "&sort=published_utc"
        + f"&published_utc.gte={start_date}"
        + f"&published_utc.lte={end_date}"
    )

    api_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)

    result = response.json()["results"]

    while "next_url" in response.json():
        new_url = response.json()["next_url"]
        response = requests.get(new_url, headers=headers)
        result += response.json()["results"]
    news = _flatten_json(result)
    return news


### financial modeling prep ###


def fmp_stock_news(
    ticker: str, start_date: str, end_date: str
) -> Iterable[tuple[ArticleContent, ArticleTickerMap]]:
    """
    get news for a given ticker using fmp

    args:
        ticker: str: The ticker.
        start_date: str %Y-%m-%d
        end_date: str %Y-%m-%d

    returns:
        list of tuples, each containing (ArticleContent, ArticleTickerMap)
    """
    articles = _fmp_news(ticker, start_date, end_date)
    results = []

    # Filter articles and collect URLs
    valid_articles = []
    urls = []
    for article in tqdm(articles, disable=logger.getEffectiveLevel() > logging.INFO):
        valid_articles.append(article)
        urls.append(article["url"])

    # Fetch all articles in parallel
    texts = _get_articles(urls)

    # Process articles with their content
    for article, text in zip(valid_articles, texts):
        if not text:
            continue

        text = _process_text(text)
        # Create the article content first
        article_content = ArticleContent.create(
            url=article.get("url", ""),
            title=article.get("title", ""),
            news_source=article.get("site", ""),
            author=article.get("author", ""),
            description=article.get("text", ""),
            published_time=datetime.datetime.strptime(
                article["publishedDate"], "%Y-%m-%d %H:%M:%S"
            ),
            date=datetime.datetime.strptime(
                article["publishedDate"], "%Y-%m-%d %H:%M:%S"
            ).date(),
            content=text,
            word_length=len(text.split()),
            char_length=len(text),
            api="fmp stock news",
        )

        # Create the ticker mapping
        article_ticker_map = ArticleTickerMap.create(
            article_id=article_content.id,
            ticker=ticker,
        )

        # Add both to results
        results.append((article_content, article_ticker_map))

    return results


def _fmp_news(ticker: str, start_date: str, end_date: str) -> Iterable:
    """
    Example output:
    [
        {
            "symbol": "AAPL",
            "publishedDate": "2024-02-28 05:55:00",
            "title": "Missed Out on Apple? Buy This Essential Supplier Instead",
            "image": "https://cdn.snapi.dev/images/v1/0/q/apple-macbook-pro-15-inch-2015-2297874.jpg",
            "site": "fool.com",
            "text": "Consumer electronics companies, including Apple, are obliged to invest in new products and, in turn, their production lines. This technology company's solutions help improve manufacturing quality and productivity.",
            "url": "https://www.fool.com/investing/2024/02/28/missed-out-on-apple-buy-this-essential-supplier-in/"
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v3/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    result = []
    article_count = 0
    page_count = 0
    limit = 50
    params = {
        "apikey": api_key,
    }
    prev_response = None

    # Calculate number of days between start and end date to adjust article limit
    date_diff = (
        datetime.datetime.strptime(end_date, "%Y-%m-%d")
        - datetime.datetime.strptime(start_date, "%Y-%m-%d")
    ).days
    max_articles = MAX_ARTICLE_COUNT_PER_DAY * max(1, date_diff)

    while article_count < max_articles:
        endpoint = (
            f"{base_url}"
            + f"stock_news?tickers={ticker}"
            + f"&page={page_count}"
            + f"&from={start_date}"
            + f"&to={end_date}"
            + f"&limit={limit}"
        )

        try:
            response_data = _make_fmp_request(endpoint, params=params)

            if not response_data:
                logger.debug(
                    f"No news found for {ticker} from {start_date} to {end_date}"
                )
                break

            if response_data == prev_response:
                logger.debug("No new news found")
                break

            result += response_data
            page_count += 1
            article_count += len(response_data)
            prev_response = response_data

        except Exception as e:
            logger.error(f"Error fetching news page {page_count}: {str(e)}")
            break

    return result


def fmp_press_release(ticker, start_date, end_date):
    """
    get press releases

    """
    base_url = FMP_BASE_URL + "/v3/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    # expect press releases to be sparse (i.e. less than 50 per day) so just get first page
    endpoint = f"{base_url}" + "press-releases" + f"/{ticker}"

    params = {
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching news: {response.status_code}")

    releases = response.json()
    results = []

    for release in releases:
        release_date = datetime.datetime.strptime(release["date"], "%Y-%m-%d %H:%M:%S")
        if (
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            <= release_date
            <= datetime.datetime.strptime(end_date, "%Y-%m-%d")
        ):
            results.append(
                PressRelease.create(
                    ticker=ticker,
                    title=release["title"],
                    date=release_date.date(),
                    content=release["text"],
                    published_time=release_date,
                )
            )

    return results


def fmp_earnings_transcript(
    ticker: str, year: int, quarter: int
) -> Iterable[EarningsTranscript]:
    """
    get earnings transcript for a given ticker using fmp

    args:
        ticker: str: The ticker.
        year: int: The year.
        quarter: int: The quarter.

    returns:
        list of EarningsTranscript
    """
    transcripts = _fmp_earnings_transcript(ticker, year, quarter)
    results = []

    for transcript in transcripts:
        logger.info(f"Processing transcript: {transcript['date']}")

        result = EarningsTranscript.create(
            ticker=ticker,
            year=year,
            quarter=quarter,
            date=datetime.datetime.strptime(transcript["date"], "%Y-%m-%d %H:%M:%S"),
            content=transcript["content"],
        )
        results.append(result)

    return results


def _fmp_earnings_transcript(ticker: str, year: int, quarter: int) -> Iterable:
    """
    Example output:
    [
        {
            "symbol": "AAPL",
            "quarter": 3,
            "year": 2020,
            "date": "2020-07-30 23:35:04",
            "content": "Operator: Good day, everyone. Welcome to the Apple Incorporated Third Quarter Fiscal Year 2020 Earnings Conference Call. Today's call is being recorded. At this time, for opening remarks and introductions, I would like to turn things over to Mr. Tejas Gala, Senior Manager, Corporate Finance and Investor Relations. Please go ahead, sir.\nTejas Gala: Thank you. Good afternoon and thank you for joining us. Speaking first today is Apple's CEO, Tim Cook; and he'll be followed by CFO, Luca Maestri. After that, we'll open the call to questions from analysts. Please note that some of the information you'll hear during our discussion today will consist of forward-looking statements including without limitation..."
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v3/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    endpoint = (
        f"{base_url}earning_call_transcript/{ticker}?year={year}&quarter={quarter}"
    )
    return _make_fmp_request(endpoint, params={"apikey": api_key})


def fmp_company_profile(tickers: Union[str, List[str]]) -> Iterable[CompanyProfile]:
    """
    get company profile for given ticker(s) using fmp

    args:
        tickers: str or List[str]: Single ticker or list of tickers.
                Multiple tickers will be processed in a single request.

    returns:
        list of CompanyProfile
    """
    # Convert single ticker to list for uniform handling
    if isinstance(tickers, str):
        tickers = [tickers]

    # Join tickers with comma for API request
    ticker_str = ",".join(tickers)
    profiles = _fmp_profile(ticker_str)
    results = []
    retrieved_date = datetime.datetime.now().date()

    for profile_data in profiles:
        result = CompanyProfile.create(
            ticker=profile_data["symbol"],
            country=profile_data["country"],
            retrieved_date=retrieved_date,
            beta=profile_data["beta"],
            company_name=profile_data["companyName"],
            cik=profile_data["cik"],
            cusip=profile_data["cusip"],
            exchange=profile_data["exchange"],
            industry=profile_data["industry"],
            website=profile_data["website"],
            description=profile_data["description"],
            sector=profile_data["sector"],
            is_etf=profile_data["isEtf"],
            is_actively_trading=profile_data["isActivelyTrading"],
            is_adr=profile_data["isAdr"],
            is_fund=profile_data["isFund"],
        )
        results.append(result)

    return results


def _fmp_profile(ticker: str) -> Iterable:
    """
    Example output:
    [
        {
            "symbol": "AAPL",
            "price": 178.72,
            "beta": 1.286802,
            "volAvg": 58405568,
            "mktCap": 2794144143933,
            "lastDiv": 0.96,
            "range": "124.17-198.23",
            "changes": -0.13,
            "companyName": "Apple Inc.",
            "currency": "USD",
            "cik": "0000320193",
            "isin": "US0378331005",
            "cusip": "037833100",
            "exchange": "NASDAQ Global Select",
            "exchangeShortName": "NASDAQ",
            "industry": "Consumer Electronics",
            "website": "https://www.apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. It also sells various related services. In addition, the company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; AirPods Max, an over-ear wireless headphone; and wearables, home, and accessories comprising AirPods, Apple TV, Apple Watch, Beats products, HomePod, and iPod touch. Further, it provides AppleCare support services; cloud services store services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts. Additionally, the company offers various services, such as Apple Arcade, a game subscription service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV+, which offers exclusive original content; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers, wholesalers, retailers, and resellers. Apple Inc. was incorporated in 1977 and is headquartered in Cupertino, California.",
            "ceo": "Mr. Timothy D. Cook",
            "sector": "Technology",
            "country": "US",
            "fullTimeEmployees": "164000",
            "phone": "408 996 1010",
            "address": "One Apple Park Way",
            "city": "Cupertino",
            "state": "CA",
            "zip": "95014",
            "dcfDiff": 4.15176,
            "dcf": 150.082,
            "image": "https://financialmodelingprep.com/image-stock/AAPL.png",
            "ipoDate": "1980-12-12",
            "defaultImage": false,
            "isEtf": false,
            "isActivelyTrading": true,
            "isAdr": false,
            "isFund": false
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v3/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    endpoint = f"{base_url}/profile/{ticker}"

    params = {
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Error fetching company profile: {response.status_code}")

    return response.json()


def fmp_company_share_float(ticker: str) -> Iterable[CompanyShareFloat]:
    """
    get company share float for a given ticker using fmp

    args:
        ticker: str: The ticker.

    returns:
        list of CompanyShareFloat
    """
    share_floats = _fmp_share_float(ticker)
    results = []

    for share_float_data in share_floats:
        if not share_float_data["date"]:
            logger.warning(f"No date found for {ticker}")
            continue

        result = CompanyShareFloat.create(
            ticker=share_float_data["symbol"],
            date=datetime.datetime.strptime(
                share_float_data["date"], "%Y-%m-%d %H:%M:%S"
            ).date(),
            free_float=share_float_data["freeFloat"],
            float_shares=share_float_data["floatShares"],
            outstanding_shares=share_float_data["outstandingShares"],
            source=share_float_data["source"],
        )
        results.append(result)

    return results


def _fmp_share_float(ticker: str) -> Iterable:
    """
    Example output:
    [
        {
            "symbol": "AAPL",
            "freeFloat": 99.89311242764762,
            "floatShares": 15891096314,
            "outstandingShares": 15908100096,
            "source": "https://www.sec.gov/Archives/edgar/data/320193/000032019322000070/aapl-20220625.htm",
            "date": "2022-11-01 08:29:30"
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v4/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    endpoint = f"{base_url}shares_float?symbol={ticker}"

    params = {
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Error fetching company share float: {response.status_code}")

    return response.json()


def fmp_price_target(ticker: str) -> Iterable[PriceTarget]:
    """
    get price target for a given ticker using fmp

    args:
        ticker: str: The ticker.

    returns:
        list of PriceTarget
    """
    price_targets = _fmp_price_target(ticker)
    results = []

    for target_data in price_targets:
        result = PriceTarget.create(
            ticker=target_data["symbol"],
            published_date=datetime.datetime.strptime(
                target_data["publishedDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).date(),  #'2023-09-18T02:36:00.000Z'
            analyst_company=target_data["analystCompany"],
            news_url=target_data["newsURL"],
            news_title=target_data["newsTitle"],
            analyst_name=target_data["analystName"],
            price_target=target_data["priceTarget"],
            adj_price_target=target_data["adjPriceTarget"],
            price_when_posted=target_data["priceWhenPosted"],
            news_publisher=target_data["newsPublisher"],
            news_base_url=target_data["newsBaseURL"],
        )
        results.append(result)

    return results


def _fmp_price_target(ticker: str) -> Iterable:
    """
    Example output:
    [
        {
            "symbol": "AAPL",
            "publishedDate": "2023-09-18T02:36:00.000Z",
            "newsURL": "https://www.benzinga.com/analyst-ratings/analyst-color/23/09/34673717/apple-analyst-says-iphone-15-pro-pro-max-preorders-strong-out-of-the-gates-increasi",
            "newsTitle": "Apple Analyst Says iPhone 15 Pro, Pro Max Preorders Strong Out Of The Gates, Increasing Confidence In Estimates For Holiday Quarter",
            "analystName": "Daniel Ives",
            "priceTarget": 240,
            "adjPriceTarget": 240,
            "priceWhenPosted": 175.01,
            "newsPublisher": "Benzinga",
            "newsBaseURL": "benzinga.com",
            "analystCompany": "Wedbush"
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v4/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    endpoint = f"{base_url}price-target?symbol={ticker}"

    params = {
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Error fetching price target: {response.status_code}")

    return response.json()


def fmp_analyst_rating_change(ticker: str) -> Iterable[AnalystRatingChange]:
    """
    get analyst rating change for a given ticker using fmp

    args:
        ticker: str: The ticker.

    returns:
        list of AnalystRatingChange
    """
    rating_changes = _fmp_analyst_rating_change(ticker)
    results = []

    for change_data in rating_changes:
        result = AnalystRatingChange.create(
            ticker=change_data["symbol"],
            published_date=datetime.datetime.strptime(
                change_data["publishedDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).date(),
            grading_company=change_data["gradingCompany"],
            news_url=change_data["newsURL"],
            news_title=change_data["newsTitle"],
            news_base_url=change_data["newsBaseURL"],
            news_publisher=change_data["newsPublisher"],
            new_grade=change_data["newGrade"],
            previous_grade=change_data["previousGrade"],
            action=change_data["action"],
            price_when_posted=change_data["priceWhenPosted"],
        )
        results.append(result)

    return results


def _fmp_analyst_rating_change(ticker: str) -> Iterable:
    """
    Example output:
    [
        {
            "symbol": "AAPL",
            "publishedDate": "2023-09-12T10:48:00.000Z",
            "newsURL": "https://www.benzinga.com/analyst-ratings/analyst-color/23/09/34490640/apple-wonderlust-iphone-15-event-will-reveal-shift-to-premium-products-analyst",
            "newsTitle": "Apple 'Wonderlust' iPhone 15 Event Will Reveal Shift To Premium Products: Analyst",
            "newsBaseURL": "benzinga.com",
            "newsPublisher": "Benzinga",
            "newGrade": "Neutral",
            "previousGrade": "Neutral",
            "gradingCompany": "Rosenblatt Securities",
            "action": "hold",
            "priceWhenPosted": 176.6009
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v4/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    endpoint = f"{base_url}upgrades-downgrades?symbol={ticker}"

    params = {
        "apikey": api_key,
    }

    response = requests.get(endpoint, params=params, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Error fetching analyst rating change: {response.status_code}")

    return response.json()


def fmp_earnings_calendar(start_date: str, end_date: str) -> Iterable[EarningsCalendar]:
    """
    get earnings calendar for a given date range using fmp

    args:
        start_date: str: The start date.
        end_date: str: The end date.

    returns:
        list of EarningsCalendar
    """
    earnings = _fmp_earnings_calendar(start_date, end_date)
    results = []

    for earnings_data in earnings:
        # skip if a symbol contains a digit or a dot - proxy for non-US symbols
        if re.search(r"\d|\.", earnings_data["symbol"]):
            continue

        result = EarningsCalendar.create(
            ticker=earnings_data["symbol"],
            fiscal_date_ending=datetime.datetime.strptime(
                earnings_data["fiscalDateEnding"], "%Y-%m-%d"
            ).date(),
            date=datetime.datetime.strptime(earnings_data["date"], "%Y-%m-%d").date(),
            eps=earnings_data["eps"],
            eps_estimated=earnings_data["epsEstimated"],
            time=earnings_data["time"],
            revenue=earnings_data["revenue"],
            revenue_estimated=earnings_data["revenueEstimated"],
            updated_from_date=datetime.datetime.strptime(
                earnings_data["updatedFromDate"], "%Y-%m-%d"
            ).date(),
        )
        results.append(result)

    return results


def _fmp_earnings_calendar(start_date: str, end_date: str) -> Iterable:
    """
    Example output:
    [
        {
            "date": "2023-08-03",
            "symbol": "AAPL",
            "eps": 1.26,
            "epsEstimated": 1.19,
            "time": "amc",
            "revenue": 81797000000,
            "revenueEstimated": 81685700000,
            "fiscalDateEnding": "2023-07-01",
            "updatedFromDate": "2024-06-30"
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v3/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    results = []
    current = start

    while current <= end:
        # Determine the start and end of the current month
        month_start = current.replace(day=1)
        next_month_start = (month_start + datetime.timedelta(days=31)).replace(day=1)
        month_end = next_month_start - datetime.timedelta(days=1)

        # Log the fetch range
        logger.info(
            f"Fetching earnings calendar data from {month_start} to {month_end}"
        )

        # Fetch data for the current month
        endpoint = f"{base_url}earning_calendar?from={month_start}&to={month_end}"

        response = requests.get(endpoint, params={"apikey": api_key})
        response.raise_for_status()  # Ensure request succeeded
        results.extend(response.json())

        # Move to the next month
        current = next_month_start

    return results


def fmp_economics_calendar(
    start_date: str, end_date: str
) -> Iterable[EconomicsCalendar]:
    """
    get economics calendar for a given date range using fmp

    args:
        start_date: str: The start date.
        end_date: str: The end date.

    returns:
        list of EconomicsCalendar
    """
    economics = _fmp_economics_calendar(start_date, end_date)
    logger.debug(f"Fetched {len(economics)} economics calendar data")

    results = []

    for economics_data in economics:
        result = EconomicsCalendar.create(
            event=economics_data["event"],
            datetime=datetime.datetime.strptime(
                economics_data["date"], "%Y-%m-%d %H:%M:%S"
            ),
            date=datetime.datetime.strptime(
                economics_data["date"], "%Y-%m-%d %H:%M:%S"
            ).date(),
            country=economics_data["country"],
            currency=economics_data["currency"],
            previous=economics_data["previous"],
            estimate=economics_data["estimate"],
            actual=economics_data["actual"],
            change=economics_data["change"],
            impact=economics_data["impact"],
            change_percentage=economics_data["changePercentage"],
            unit=economics_data["unit"],
        )
        results.append(result)
    return results


def _fmp_economics_calendar(start_date: str, end_date: str) -> Iterable:
    """
    Example output:
    [
        {
            "date": "2023-10-11 03:35:00",
            "country": "JP",
            "event": "5-Year JGB Auction",
            "currency": "JPY",
            "previous": 0.291,
            "estimate": null,
            "actual": 0.33,
            "change": 0.039,
            "impact": "Low",
            "changePercentage": 13.402,
            "unit": "%"
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v3/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    results = []
    current = start

    while current <= end:
        # Determine the start and end of the current month
        month_start = current.replace(day=1)
        next_month_start = (month_start + datetime.timedelta(days=31)).replace(day=1)
        month_end = next_month_start - datetime.timedelta(days=1)
        # Log the fetch range
        logger.info(
            f"Fetching economics calendar data from {month_start} to {month_end}"
        )

        # Fetch data for the current month
        endpoint = f"{base_url}economic_calendar?from={month_start}&to={month_end}"

        response = requests.get(endpoint, params={"apikey": api_key})
        response.raise_for_status()  # Ensure request succeeded
        results.extend(response.json())

        # Move to the next month
        current = next_month_start

    return results


def fmp_economic_indicators(
    name: str, start_date: str, end_date: str
) -> Iterable[EconomicIndicator]:
    """
    get economic indicators for a given date range using fmp

    args:
        name: str: The name of the economic indicator.
        start_date: str: The start date.
        end_date: str: The end date.

    returns:
        list of EconomicIndicator
    """
    indicators = _fmp_economic_indicators(name, start_date, end_date)
    results = []

    for indicator_data in indicators:
        result = EconomicIndicator.create(
            name=name,
            date=datetime.datetime.strptime(indicator_data["date"], "%Y-%m-%d").date(),
            value=indicator_data["value"],
        )
        results.append(result)

    return results


def _fmp_economic_indicators(name: str, start_date: str, end_date: str) -> Iterable:
    """
    Example output:
    [
        {
            "date": "2022-04-01",
            "value": "24882.878"
        },
        {
            "date": "2022-01-01",
            "value": "24386.734"
        }
    ]
    """

    base_url = FMP_BASE_URL + "/v4/"
    api_key = os.getenv("FMP_ACCESS_KEY")

    endpoint = f"{base_url}economic?name={name}&from={start_date}&to={end_date}"

    try:
        return _make_fmp_request(endpoint, params={"apikey": api_key})
    except Exception as e:
        logger.error(f"Error fetching economic indicators: {str(e)}")
        return []


### requests ###


async def _get_article_async(url: str, session: aiohttp.ClientSession) -> str:
    """Async version of article fetching"""
    # Use pre-loaded skip list

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    try:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                logger.warning(
                    f"Unable to retrieve article from {url}, status code: {response.status}"
                )
                return ""
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            return " ".join([p.text for p in soup.find_all("p")])
    except Exception as e:
        logger.warning(f"Error fetching {url}: {e}")
        return ""


async def _get_articles_batch(urls: List[str]) -> List[str]:
    """Fetch multiple articles in parallel"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        # Process in batches to avoid too many concurrent connections
        for i in range(0, len(urls), MAX_CONCURRENT_REQUESTS):
            batch = urls[i : i + MAX_CONCURRENT_REQUESTS]
            batch_tasks = [_get_article_async(url, session) for url in batch]
            tasks.extend(batch_tasks)
        return await asyncio.gather(*tasks)


def _get_articles(urls: List[str]) -> List[str]:
    """Wrapper to run async article fetching"""
    return asyncio.run(_get_articles_batch(urls))


def _flatten_json(options: Iterable) -> Iterable:
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
    return res


# preprocessing pipeline


def _process_text(text: str) -> str:
    """
    regex removes space
    keep only long sentences from the original article
    """
    text = _regex(text)
    text = _keep_long_sentences(text)
    return text


def _regex(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\t+", " ", text)
    return text


def _keep_long_sentences(text: str, length: int = 8) -> str:
    return text[:LENGTH_LIMIT]


def _contains_financial_entities(text: str) -> bool:
    return True


def _contains_keywords(text: str) -> bool:
    keywords = [
        "stock",
        "earnings",
        "investment",
        "market",
        "price",
        "trading",
        "profit",
        "revenue",
        "financial",
        "quarter",
        "report",
        "analyst",
        "forecast",
        "valuation",
    ]
    return any(keyword in text for keyword in keywords)


def _is_relevant(text: str, title: str, ticker: str, is_whitelisted: bool = False):
    """make sure the key word is indeed featured in the article"""

    if is_whitelisted:
        return True, "Whitelisted source"

    text = text.lower()
    title = title.lower()

    # check if the company name is in the title
    if ticker.lower() in title:
        return True, "Title contains stock name / ticker"

    # check if the company name is in the article more than once
    if len(re.findall(ticker.lower(), text)) < 1:
        return False, "Ticker shows up less than once"

    # check if the company name is in the first 100 words
    words = text.split(" ")[0:100]
    if ticker.lower() not in words:
        return False, "Financial keyword not in the first 100 words"

    # check if the article contains financial entities or keywords
    if (not _contains_financial_entities(text)) and (not _contains_keywords(text)):
        return False, "Does not contain financial entities or keywords"

    return True, "All tests passed"


def _make_fmp_request(endpoint: str, params: dict = None) -> dict:
    """Helper function to make FMP API requests with retries and timeout"""
    if params is None:
        params = {}

    max_retries = 3
    base_timeout = 30  # seconds
    retry_delay = 60  # seconds between retries
    rate_limit_delay = 60  # seconds to wait when hitting rate limit

    # Use session to properly handle connection pooling and SSL
    session = requests.Session()

    for attempt in range(max_retries):
        try:
            response = session.get(
                endpoint,
                params=params,
                timeout=base_timeout,
                verify=True,  # Enable SSL verification
            )

            # Check specifically for rate limit
            if response.status_code == 429:
                logger.warning(
                    f"Rate limit hit, waiting {rate_limit_delay} seconds before retry..."
                )
                time.sleep(rate_limit_delay)
                continue

            response.raise_for_status()
            return response.json()
        except (requests.Timeout, requests.RequestException) as e:
            if attempt == max_retries - 1:
                logger.error(f"Request failed after {max_retries} attempts: {str(e)}")
                if "429" in str(e):
                    return (
                        []
                    )  # Return empty list for rate limit errors after all retries
                raise

            logger.warning(
                f"Request failed on attempt {attempt + 1}, waiting {retry_delay} seconds before retry..."
            )
            time.sleep(retry_delay)  # Wait 60 seconds before next retry
            continue
        finally:
            session.close()  # Ensure we clean up the session
