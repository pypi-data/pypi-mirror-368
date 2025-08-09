"""
database table and schema
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime,
    Boolean,
    Date,
    Float,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


def generate_deterministic_uuid(*components: str) -> uuid.UUID:
    """Generate a deterministic UUID from one or more string components.

    Args:
        *components: One or more strings to use for generating the UUID

    Returns:
        A UUID that will be the same every time for the same input components

    Example:
        >>> generate_deterministic_uuid("example.com")
        UUID('1234...')
        >>> generate_deterministic_uuid("AAPL", "Q1 Earnings", "2024-01-01")
        UUID('5678...')
    """
    # Join all components with a delimiter that won't appear in the components
    key = "||".join(str(c) for c in components)
    # Use UUID namespace for URLs since it's a standard namespace
    return uuid.uuid5(uuid.NAMESPACE_URL, key)


# Define the base class
Base = declarative_base()  # register meta-data of data tables


# Articles table => data table name in database
class ArticleContent(Base):
    __tablename__ = "article_content"

    id = Column(UUID(as_uuid=True), primary_key=True)  # Changed from String to UUID
    news_source = Column(String)
    author = Column(String)
    title = Column(String)
    description = Column(Text)
    url = Column(String, unique=True)  # URL is unique for each article
    published_time = Column(DateTime)
    date = Column(Date)
    content = Column(Text)
    word_length = Column(Integer)
    char_length = Column(Integer)
    api = Column(String)
    eco_event_id = Column(
        UUID(as_uuid=True), ForeignKey("economics_calendar.id"), nullable=True
    )

    # Define relationship to EconomicsCalendar
    economics_event = relationship("EconomicsCalendar", backref="related_articles")

    @classmethod
    def create(cls, url: str, title: str, **kwargs):
        """
        Create an article content entry with a deterministic UUID based on URL

        Args:
            url: Article URL (unique identifier)
            title: Article title
            **kwargs: Additional article attributes including optional eco_event_id
        """
        return cls(
            id=generate_deterministic_uuid(url),
            url=url,
            title=title,
            **kwargs,
        )

    def __repr__(self):
        if self.title:
            title = self.title[:20] + "..."
        else:
            title = "No Title"
        return f"<ArticleContent(id='{self.id}', title='{title}')>"


class ArticleTickerMap(Base):
    __tablename__ = "article_ticker_map"

    article_id = Column(
        UUID(as_uuid=True), ForeignKey("article_content.id"), primary_key=True
    )
    ticker = Column(String, primary_key=True)

    # Relationship to ArticleContent
    article = relationship("ArticleContent", backref="ticker_maps")

    @classmethod
    def create(cls, article_id: uuid.UUID, ticker: str):
        """
        Create an article-ticker mapping

        Args:
            article_id: UUID of the article content
            ticker: Company ticker symbol
        """
        return cls(
            article_id=article_id,
            ticker=ticker,
        )

    def __repr__(self):
        return f"<ArticleTickerMap(article_id='{self.article_id}', ticker='{self.ticker}')>"


class PressRelease(Base):
    __tablename__ = "press_releases"

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String)
    content = Column(Text)
    published_time = Column(DateTime)
    date = Column(Date)
    ticker = Column(String)

    @classmethod
    def create(cls, ticker: str, title: str, date: Date, **kwargs):
        """
        Create a press release with a unique ID based on ticker, title, and date

        Args:
            ticker: Company ticker symbol
            title: Press release title
            date: Press release date
            **kwargs: Additional press release attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, title, str(date)),
            ticker=ticker,
            title=title,
            date=date,
            **kwargs,
        )

    def __repr__(self):
        if self.title:
            title = self.title[:20] + "..."
        else:
            title = "No Title"
        return f"<PressRelease(id='{self.id}', title='{title}...')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class EarningsTranscript(Base):
    __tablename__ = "earnings_transcript"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    year = Column(Integer)
    quarter = Column(Integer)
    date = Column(Date)
    content = Column(Text)

    def __init__(self, id, ticker, year, quarter, date, content):
        self.id = id
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.date = date
        self.content = content

    @classmethod
    def create(cls, ticker: str, year: int, quarter: int, **kwargs):
        """
        Create an earnings transcript with a unique ID based on ticker, year, and quarter

        Args:
            ticker: Company ticker symbol
            year: Fiscal year
            quarter: Fiscal quarter
            **kwargs: Additional transcript attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, str(year), str(quarter)),
            ticker=ticker,
            year=year,
            quarter=quarter,
            **kwargs,
        )

    def __repr__(self):
        return f"<EarningsTranscript {self.ticker} Q{self.quarter} {self.year}>"


class CompanyProfile(Base):
    __tablename__ = "company_profile"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    beta = Column(String)
    company_name = Column(String)
    cik = Column(String)
    cusip = Column(String)
    exchange = Column(String)
    industry = Column(String)
    website = Column(String)
    description = Column(Text)
    sector = Column(String)
    country = Column(String)
    is_etf = Column(Boolean)
    is_actively_trading = Column(Boolean)
    is_adr = Column(Boolean)
    is_fund = Column(Boolean)
    retrieved_date = Column(Date)

    @classmethod
    def create(cls, ticker: str, country: str, retrieved_date: Date, **kwargs):
        """
        Create a company profile with a unique ID based on ticker, country and date

        Args:
            ticker: Company ticker symbol
            country: Company's country
            retrieved_date: Date when the profile was retrieved
            **kwargs: Additional profile attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, country, str(retrieved_date)),
            ticker=ticker,
            country=country,
            retrieved_date=retrieved_date,
            **kwargs,
        )

    def __repr__(self):
        return f"<CompanyProfile(ticker='{self.ticker}', company_name='{self.company_name}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class CompanyShareFloat(Base):
    __tablename__ = "company_share_float"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    free_float = Column(Float)
    float_shares = Column(BigInteger)
    outstanding_shares = Column(BigInteger)
    source = Column(String)
    date = Column(Date)

    @classmethod
    def create(cls, ticker: str, date: Date, **kwargs):
        """
        Create a company share float with a unique ID based on ticker and date

        Args:
            ticker: Company ticker symbol
            date: Data date
            **kwargs: Additional share float attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, str(date)),
            ticker=ticker,
            date=date,
            **kwargs,
        )

    def __repr__(self):
        return f"<CompanyShareFloat(ticker='{self.ticker}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class PriceTarget(Base):
    __tablename__ = "price_target"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    published_date = Column(Date)
    news_url = Column(String)
    news_title = Column(String)
    analyst_name = Column(String)
    price_target = Column(Float)
    adj_price_target = Column(Float)
    price_when_posted = Column(Float)
    news_publisher = Column(String)
    news_base_url = Column(String)
    analyst_company = Column(String)

    @classmethod
    def create(cls, ticker: str, published_date: Date, analyst_company: str, **kwargs):
        """
        Create a price target with a unique ID based on ticker, published date, and analyst company

        Args:
            ticker: Company ticker symbol
            published_date: Publication date
            analyst_company: Company providing the price target
            **kwargs: Additional price target attributes
        """
        return cls(
            id=generate_deterministic_uuid(
                ticker, str(published_date), analyst_company
            ),
            ticker=ticker,
            published_date=published_date,
            analyst_company=analyst_company,
            **kwargs,
        )

    def __repr__(self):
        return f"<PriceTarget(ticker='{self.ticker}', published_date='{self.published_date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class AnalystRatingChange(Base):
    __tablename__ = "analyst_rating_change"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    published_date = Column(Date)
    news_url = Column(String)
    news_title = Column(String)
    news_base_url = Column(String)
    news_publisher = Column(String)
    new_grade = Column(String)
    previous_grade = Column(String)
    grading_company = Column(String)
    action = Column(String)
    price_when_posted = Column(Float)

    @classmethod
    def create(cls, ticker: str, published_date: str, grading_company: str, **kwargs):
        """
        Create an analyst rating change with a unique ID based on ticker, published date, and grading company

        Args:
            ticker: Company ticker symbol
            published_date: Publication date
            grading_company: Company providing the rating
            **kwargs: Additional rating change attributes
        """
        return cls(
            id=generate_deterministic_uuid(
                ticker, str(published_date), grading_company
            ),
            ticker=ticker,
            published_date=published_date,
            grading_company=grading_company,
            **kwargs,
        )

    def __repr__(self):
        return f"<AnalystRatingChange(ticker='{self.ticker}', published_date='{self.published_date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class EarningsCalendar(Base):
    __tablename__ = "earnings_calendar"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    date = Column(Date)
    eps = Column(Float)
    eps_estimated = Column(Float)
    time = Column(String)
    revenue = Column(Float)
    revenue_estimated = Column(Float)
    fiscal_date_ending = Column(Date)
    updated_from_date = Column(Date)

    @classmethod
    def create(cls, ticker: str, fiscal_date_ending: str, **kwargs):
        """
        Create an earnings calendar entry with a unique ID based on ticker and date

        Args:
            ticker: Company ticker symbol
            date: Earnings date
            **kwargs: Additional earnings calendar attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, str(fiscal_date_ending)),
            ticker=ticker,
            fiscal_date_ending=fiscal_date_ending,
            **kwargs,
        )

    def __repr__(self):
        return f"<EarningsCalendar(ticker='{self.ticker}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class EconomicsCalendar(Base):
    __tablename__ = "economics_calendar"

    id = Column(UUID(as_uuid=True), primary_key=True)
    date = Column(Date)
    datetime = Column(DateTime)
    country = Column(String)
    event = Column(String)
    currency = Column(String)
    previous = Column(Float)
    estimate = Column(Float)
    actual = Column(Float)
    change = Column(Float)
    impact = Column(String)
    change_percentage = Column(Float)
    unit = Column(String)

    @classmethod
    def create(cls, event: str, datetime: DateTime, country: str, **kwargs):
        """
        Create an economics calendar entry with a unique ID based on event and date.
        Event name is standardized to title case to avoid duplicate entries.

        Args:
            event: Economic event name
            datetime: Event datetime
            country: Event country
            **kwargs: Additional economics calendar attributes
        """
        # Standardize event name capitalization
        standardized_event = event.title()

        return cls(
            id=generate_deterministic_uuid(standardized_event, str(datetime), country),
            event=event,  # Keep original event name in the record
            datetime=datetime,
            country=country,
            **kwargs,
        )

    def __repr__(self):
        return f"<EconomicsCalendar(event='{self.event}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class EconomicIndicator(Base):
    __tablename__ = "economic_indicators"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String)
    date = Column(Date)
    value = Column(String)

    @classmethod
    def create(cls, name: str, date: Date, **kwargs):
        """
        Create an economic indicator with a unique ID based on name and date

        Args:
            name: Indicator name
            date: Data date
            **kwargs: Additional indicator attributes
        """
        return cls(
            id=generate_deterministic_uuid(name, str(date)),
            name=name,
            date=date,
            **kwargs,
        )

    def __repr__(self):
        return f"<EconomicIndicator(name='{self.name}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class StockGroupedDaily(Base):
    __tablename__ = "stock_grouped_daily"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    volume = Column(Float)
    vwap = Column(Float)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    timestamp = Column(String)  # Unix timestamp in milliseconds stored as string
    num_trades = Column(Float)
    datetimes = Column(DateTime)
    date = Column(Date)
    raw_symbol = Column(String)

    @classmethod
    def create(cls, ticker: str, date: Date, **kwargs):
        """
        Create a stock daily record with a unique ID based on ticker and date

        Args:
            ticker: Stock ticker symbol
            date: Trading date
            **kwargs: Additional stock data attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, str(date)),
            ticker=ticker,
            date=date,
            **kwargs,
        )

    def __repr__(self):
        return f"<StockGroupedDaily(ticker='{self.ticker}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class RelatedCompanies(Base):
    __tablename__ = "related_companies"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)
    peers = Column(String)  # Pipe-separated list of peer tickers
    date = Column(Date)
    source = Column(String)

    @classmethod
    def create(cls, ticker: str, date: Date, source: str, **kwargs):
        """
        Create a related companies record with a unique ID based on ticker, date, and source

        Args:
            ticker: Stock ticker symbol
            date: Data date
            source: Data source (e.g. 'polygon')
            **kwargs: Additional attributes
        """
        return cls(
            id=generate_deterministic_uuid(ticker, str(date), source),
            ticker=ticker,
            date=date,
            source=source,
            **kwargs,
        )

    def __repr__(self):
        return f"<RelatedCompanies(ticker='{self.ticker}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class OptionsChainSnapshot(Base):
    __tablename__ = "options_chain_snapshot"

    id = Column(UUID(as_uuid=True), primary_key=True)
    ticker = Column(String)  # Underlying stock ticker
    osi = Column(String)  # Option symbol identifier
    date = Column(Date)  # Date of the snapshot
    last_updated = Column(String)  # Unix timestamp in milliseconds stored as string

    # Price data
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    previous_close = Column(Float)
    change = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float)
    vwap = Column(Float)

    # Option specific data
    strike_price = Column(Float)
    expiration_date = Column(Date)
    contract_type = Column(String)  # 'call' or 'put'
    open_interest = Column(Float)

    # Greeks
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    implied_volatility = Column(Float)

    @classmethod
    def create(cls, osi: str, date: datetime.date, **kwargs):
        """
        Create an options chain snapshot with a unique ID based on OSI, date, and last_updated

        Args:
            osi: Option Symbol Identifier
            date: Date of the snapshot
            **kwargs: Additional options data attributes
        """
        # Include last_updated in the UUID generation to ensure uniqueness
        last_updated = kwargs.get("last_updated", "")
        return cls(
            id=generate_deterministic_uuid(osi, str(date), str(last_updated)),
            osi=osi,
            date=date,
            **kwargs,
        )

    def __repr__(self):
        return f"<OptionsChainSnapshot(osi='{self.osi}', date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class TreasuryYield(Base):
    __tablename__ = "treasury_yield"

    id = Column(UUID(as_uuid=True), primary_key=True)
    date = Column(Date)
    month1 = Column(Float)
    month2 = Column(Float)
    month3 = Column(Float)
    month6 = Column(Float)
    year1 = Column(Float)
    year2 = Column(Float)
    year3 = Column(Float)
    year5 = Column(Float)
    year7 = Column(Float)
    year10 = Column(Float)
    year20 = Column(Float)
    year30 = Column(Float)

    @classmethod
    def create(cls, date: Date, **kwargs):
        """
        Create a treasury yield record with a unique ID based on date

        Args:
            date: Data date
            **kwargs: Additional treasury yield attributes for different durations
        """
        return cls(
            id=generate_deterministic_uuid(str(date)),
            date=date,
            **kwargs,
        )

    def __repr__(self):
        return f"<TreasuryYield(date='{self.date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()


class DailyEcoSummary(Base):
    __tablename__ = "daily_eco_summary"

    id = Column(UUID(as_uuid=True), primary_key=True)
    eco_event_id = Column(UUID(as_uuid=True), ForeignKey("economics_calendar.id"))
    summary = Column(Text)
    update_date = Column(Date)

    # Relationship to EconomicsCalendar
    economics_event = relationship("EconomicsCalendar", backref="summaries")

    @classmethod
    def create(cls, eco_event_id: uuid.UUID, update_date: Date, **kwargs):
        """
        Create a daily economic summary with a unique ID based on event ID and update date

        Args:
            eco_event_id: UUID of the economics calendar event
            update_date: Date when the summary was created/updated
            **kwargs: Additional summary attributes
        """
        return cls(
            id=generate_deterministic_uuid(str(eco_event_id), str(update_date)),
            eco_event_id=eco_event_id,
            update_date=update_date,
            **kwargs,
        )

    def __repr__(self):
        return f"<DailyEcoSummary(event_id='{self.eco_event_id}', update_date='{self.update_date}')>"

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Attribute '{key}' not found")

    def __iter__(self):
        for column in self.__table__.columns:
            yield column.name, getattr(self, column.name)

    def items(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }.items()
