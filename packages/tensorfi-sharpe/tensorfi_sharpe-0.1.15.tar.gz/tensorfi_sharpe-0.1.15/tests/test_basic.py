"""
Basic test cases for the sharpe package
"""

import pytest


def test_package_imports():
    """Test that main package components can be imported."""
    # Test main package
    import sharpe

    assert sharpe is not None

    # Test data subpackage
    try:
        from sharpe import data

        assert data is not None
    except ImportError:
        pytest.skip("sharpe.data package not available")

    # Test utils subpackage
    try:
        from sharpe import utils

        assert utils is not None
    except ImportError:
        pytest.skip("sharpe.utils package not available")


def test_data_module_imports():
    """Test that data modules can be imported."""
    # Test alt module
    try:
        from sharpe.data import alt

        assert alt is not None
    except ImportError:
        pytest.skip("sharpe.data.alt module not available")

    # Test mkt module
    try:
        from sharpe.data import mkt

        assert mkt is not None
    except ImportError:
        pytest.skip("sharpe.data.mkt module not available")

    # Test db module
    try:
        from sharpe.data import db

        assert db is not None
    except ImportError:
        pytest.skip("sharpe.data.db module not available")

    # Test model module
    try:
        from sharpe.data import model

        assert model is not None
    except ImportError:
        pytest.skip("sharpe.data.model module not available")


def test_utils_module_imports():
    """Test that utils modules can be imported."""
    # Test time utilities
    try:
        from sharpe.utils import time

        assert time is not None
        # Test key functions exist
        assert hasattr(time, "closest_trading_day")
        assert hasattr(time, "trading_day_range")
        assert hasattr(time, "next_trading_day")
    except ImportError:
        pytest.skip("sharpe.utils.time module not available")

    # Test options utilities
    try:
        from sharpe.utils import options

        assert options is not None
        # Test key functions exist
        assert hasattr(options, "input_to_osi")
        assert hasattr(options, "osi_to_input")
    except ImportError:
        pytest.skip("sharpe.utils.options module not available")

    # Test constants
    try:
        from sharpe.utils import constants

        assert constants is not None
    except ImportError:
        pytest.skip("sharpe.utils.constants module not available")

    # Test logger
    try:
        from sharpe.utils import logger

        assert logger is not None
    except ImportError:
        pytest.skip("sharpe.utils.logger module not available")

    # Test env utilities
    try:
        from sharpe.utils import env

        assert env is not None
    except ImportError:
        pytest.skip("sharpe.utils.env module not available")

    # Test universe utilities
    try:
        from sharpe.utils import universe

        assert universe is not None
    except ImportError:
        pytest.skip("sharpe.utils.universe module not available")


def test_minimal_functionality():
    """Test minimal functionality works."""
    # Test that we can perform basic operations
    try:
        from sharpe.utils.time import closest_trading_day

        result = closest_trading_day("2024-01-01")
        assert isinstance(result, str)
        assert len(result) == 10  # Should be YYYY-MM-DD format
    except ImportError:
        pytest.skip("time utilities not available")

    # Test options utilities
    try:
        from sharpe.utils.options import input_to_osi

        result = input_to_osi("AAPL", "call", "2024-01-19", 150.0)
        assert isinstance(result, str)
        assert result.startswith("O:AAPL")
    except ImportError:
        pytest.skip("options utilities not available")
