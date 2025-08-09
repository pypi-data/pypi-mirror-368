# Sharpe - Financial Data & Analysis Library

A Python library for financial data access, market analysis, and options calculations.

Wrappers around Polygon and Financial Modeling Prep.

## Features

- **Market Data**: Stock prices, options data, and historical information
- **Alternative Data**: News, earnings, and company profiles
- **Options Calculations**: Black-Scholes pricing and Greeks
- **Database Integration**: PostgreSQL with async support
- **AWS Integration**: Cloud data retrieval

## Installation

```bash
# From source
git clone https://github.com/wang-sanity/sharpe.git
cd sharpe
pip install -e .

# Using conda
conda env create -f environment.yml
conda activate tensorfi-sharpe
```

## Quick Start

```python
from sharpe.data import mkt, alt
from sharpe.utils import options, time, universe

# Get market data using aggregates
data = mkt.aggregates(
    ticker="AAPL",
    multiplier=1,
    timespan="day",
    from="2024-01-01",
    to="2024-01-31"
)

# Get options chain for a ticker
options_data = mkt.options_chain("SPY")

# Work with time utilities
trading_day = time.closest_trading_day_now()
is_trading = time.is_trading_day("2024-01-15")

# Get universe of stocks
top_stocks = universe.get_top_n_traded_stock(n=50)
```

## Package Structure

- `sharpe/data/` - Market and alternative data access, database operations
- `sharpe/utils/` - Options calculations, time utilities, universe management

## Requirements

- Python 3.11+
- Core: pandas, numpy, scipy, sqlalchemy
- Optional: PostgreSQL, AWS credentials

## Development

```bash
# Setup
conda env create -f environment.yml
conda activate tensorfi-sharpe
pip install -e .[dev]

# Test
pytest
```

## Performance tuning

The data layer uses a pooled HTTP client and optional on-disk cache to reduce duplicated network calls during simulations.

- SHARPE_HTTP_CACHE_ENABLED: set to `0` to disable (default `1`)
- SHARPE_HTTP_CACHE_TTL_SECONDS: cache TTL in seconds (default `86400`)
- SHARPE_HTTP_CACHE_DIR: directory for cached responses (default `~/.cache/sharpe/http`)

These affect `sharpe.data.mkt.aggregates` and `sharpe.data.mkt.option_definition` calls extensively used by options utilities.

## License

CC BY-NC 4.0 License - see [LICENSE](LICENSE) file for details.

---

**Disclaimer**: For educational and research purposes only. Consult qualified professionals before making investment decisions.
