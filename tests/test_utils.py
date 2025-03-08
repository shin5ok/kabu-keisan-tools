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


@patch('utils.requests.get')
def test_initialize_exchange_rates(mock_get):
    """Test initialize_exchange_rates function."""
    # Create a mock response
    mock_response = MagicMock()
    mock_response.content = """
    <html>
    <table>
        <tr>
            <th>日付</th>
            <th>1月</th>
            <th>2月</th>
        </tr>
        <tr>
            <th>1</th>
            <td class="20240101">150.50</td>
            <td class="20240201">148.75</td>
        </tr>
        <tr>
            <th>2</th>
            <td class="20240102">151.25</td>
            <td class="20240202">149.00</td>
        </tr>
    </table>
    </html>
    """
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    # Reset the global variables
    utils.exchange_rates = {}
    utils.sample_html = ""
    
    # Call the function
    utils.initialize_exchange_rates()
    
    # Check if exchange_rates contains expected data
    assert '20240101' in utils.exchange_rates
    assert utils.exchange_rates['20240101'] == 150.50
    assert '20240201' in utils.exchange_rates
    assert utils.exchange_rates['20240201'] == 148.75


def test_get_exchange_rate():
    """Test get_exchange_rate function."""
    # Setup mock exchange rates
    utils.exchange_rates = {
        '20240101': 150.50,
        '20240102': 151.25,
    }
    
    # Test existing date
    with patch('utils.initialize_exchange_rates'):
        rate = utils.get_exchange_rate('20240101')
        assert rate == 150.50
    
    # Test non-existing date
    with patch('utils.initialize_exchange_rates'):
        rate = utils.get_exchange_rate('20240103')
        assert rate is None


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
