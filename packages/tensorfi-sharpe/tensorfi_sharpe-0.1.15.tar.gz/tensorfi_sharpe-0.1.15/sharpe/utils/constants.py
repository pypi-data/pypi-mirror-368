"""
constants
"""

AZURE_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

# API Base URLs
FMP_BASE_URL = "https://financialmodelingprep.com/api"  # dont add version number here
POLYGON_BASE_URL = "https://api.polygon.io"  # dont add version number here


# Price data column mappings
PX_RENAME_COLS = {
    "c": "close",
    "h": "high",
    "l": "low",
    "o": "open",
    "t": "timestamp",
    "v": "volume",
    "vw": "vwap",
    "n": "num_trades",
    "T": "ticker",
}

# API pagination limit
PAGINATE_LIMIT = 10

# Delta bucket ranges for options analysis
DELTA_BUCKET_RANGES = [0, 0.15, 0.35, 0.55, 0.7, 1]

MAX_ARTICLE_LENGTH = 20000
