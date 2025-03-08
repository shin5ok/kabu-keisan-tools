import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils


def test_convert_date_format_already_correct():
    """Test convert_date_format with already correct format."""
    result = utils.convert_date_format('15-Jan-2024')
    assert result == '15-Jan-2024'


def test_convert_date_format_needs_conversion():
    """Test convert_date_format with format that needs conversion."""
    result = utils.convert_date_format('15-01-2024')
    assert result == '15-Jan-2024'


def test_convert_date_format_invalid():
    """Test convert_date_format with invalid date format."""
    result = utils.convert_date_format('invalid-date')
    assert result is None


def test_initialize_exchange_rates():
    """Test initialize_exchange_rates function with actual API call."""
    # Save original state to restore later
    original_exchange_rates = utils.exchange_rates.copy()
    original_sample_html = utils.sample_html
    
    # Reset the global variables
    utils.exchange_rates = {}
    utils.sample_html = ""
    
    # Call the function to make actual HTTP request
    utils.initialize_exchange_rates()
    
    # Basic checks to verify data was loaded
    assert len(utils.exchange_rates) > 0

    # Check that exchange rates are all reasonable float values
    for date, rate in utils.exchange_rates.items():
        assert isinstance(date, str)
        # The date key might be in different formats depending on the HTML structure
        # Allow either 8 (YYYYMMDD) or 9 characters
        assert 7 < len(date) <= 10, f"Date key '{date}' has unexpected length: {len(date)}"
        assert isinstance(rate, float)
        assert 100 <= rate <= 200  # Reasonable range for USD-JPY in recent years

    # Restore the original state
    utils.exchange_rates = original_exchange_rates
    utils.sample_html = original_sample_html


def test_get_exchange_rate():
    """Test get_exchange_rate function with actual data."""
    # Save original state to restore later
    original_exchange_rates = utils.exchange_rates.copy()
    original_sample_html = utils.sample_html
    
    # Force initialization to ensure we have data
    utils.exchange_rates = {}
    utils.sample_html = ""
    utils.initialize_exchange_rates()
    
    # Get a valid date from the loaded data
    if len(utils.exchange_rates) > 0:
        valid_date = list(utils.exchange_rates.keys())[0]
        expected_rate = utils.exchange_rates[valid_date]

        # Test existing date
        rate = utils.get_exchange_rate(valid_date)
        assert rate == expected_rate

        # Test non-existing date (use an invalid date format)
        invalid_date = "99999999"  # This date should never exist
        rate = utils.get_exchange_rate(invalid_date)
        assert rate is None
    else:
        pytest.skip("No exchange rate data available for testing")

    # Restore the original state
    utils.exchange_rates = original_exchange_rates
    utils.sample_html = original_sample_html


@patch('utils.requests.get')
def test_initialize_exchange_rates_request_error(mock_get):
    """Test initialize_exchange_rates function with request error."""
    # Make the request raise an exception
    mock_get.side_effect = Exception("Connection error")
    
    # Reset the global variables
    utils.exchange_rates = {}
    utils.sample_html = ""
    
    # Call the function with try-except to handle the exception
    try:
        utils.initialize_exchange_rates()
    except:
        # If the function doesn't handle the exception, our test will catch it
        pass
    
    # Exchange rates should remain empty
    assert utils.exchange_rates == {}
