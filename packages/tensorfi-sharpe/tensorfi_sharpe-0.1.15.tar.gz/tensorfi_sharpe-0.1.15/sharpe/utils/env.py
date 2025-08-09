import os
from dotenv import load_dotenv
from .logger import get_logger

logger = get_logger(__name__)


def load_env():
    """Load environment variables from .env file."""
    load_dotenv(override=True)
    logger.debug("Loaded environment variables from .env file.")
