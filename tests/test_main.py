import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return """Date,Quantity,Price
15-01-2024,100,$150.50
16-Jan-2024,200,$200.25
"""


@pytest.fixture
def sample_csv_data_vest_date():
    """Sample CSV data with 'Vest Date' column instead of 'Date'."""
    return """Vest Date,Quantity,Price
15-01-2024,100,$150.50
16-Jan-2024,200,$200.25
"""


@patch('sys.stdout', new_callable=StringIO)
@patch('utils.get_exchange_rate')
@patch('utils.convert_date_format')
def test_calculate_total_value(mock_convert_date, mock_get_rate, mock_stdout, sample_csv_data):
    """Test calculate_total_value function with sample data."""
    # Setup mocks
    mock_convert_date.side_effect = lambda date_str: '15-Jan-2024' if date_str == '15-01-2024' else date_str
    mock_get_rate.return_value = 150.0
    
    # Call the function
    main.calculate_total_value(sample_csv_data)
    
    # Check output
    output = mock_stdout.getvalue()
    
    # Verify total calculation is correct
    # 100 shares at $150.50 = $15,050 * 150 JPY/USD = 2,257,500 JPY
    # 200 shares at $200.25 = $40,050 * 150 JPY/USD = 6,007,500 JPY
    # Total: 8,265,000 JPY
    assert "総額: ¥8,265,000.00" in output
    
    # Verify detailed calculations are present
    assert "株のVest詳細" in output
    assert "数量: 100.000株" in output
    assert "数量: 200.000株" in output
    assert "価格: $150.50" in output
    assert "価格: $200.25" in output
    assert "為替レート: ¥150.00" in output
    
    # Verify calculation formulas are present
    assert "USD: 150.5 * Quantity: 100" in output
    assert "USD: 200.25 * Quantity: 200" in output


@patch('sys.stdout', new_callable=StringIO)
@patch('utils.get_exchange_rate')
@patch('utils.convert_date_format')
def test_calculate_total_value_vest_date_column(mock_convert_date, mock_get_rate, mock_stdout, sample_csv_data_vest_date):
    """Test calculate_total_value function with 'Vest Date' column."""
    # Setup mocks
    mock_convert_date.side_effect = lambda date_str: '15-Jan-2024' if date_str == '15-01-2024' else date_str
    mock_get_rate.return_value = 150.0
    
    # Call the function
    main.calculate_total_value(sample_csv_data_vest_date)
    
    # Check output
    output = mock_stdout.getvalue()
    
    # Verify it works with 'Vest Date' column instead of 'Date'
    assert "総額: ¥8,265,000.00" in output
    assert "株のVest詳細" in output


@patch('sys.stdout', new_callable=StringIO)
@patch('utils.get_exchange_rate')
@patch('utils.convert_date_format')
def test_calculate_total_value_different_rates(mock_convert_date, mock_get_rate, mock_stdout, sample_csv_data):
    """Test calculate_total_value function with different exchange rates."""
    # Setup mocks
    mock_convert_date.side_effect = lambda x: x  # Identity function
    
    # Different rates for different dates
    def get_rate_side_effect(date_key):
        if date_key == '20240115':  # For 15-Jan-2024
            return 145.0
        elif date_key == '20240116':  # For 16-Jan-2024
            return 147.5
        return None
    
    mock_get_rate.side_effect = get_rate_side_effect
    
    # Mock datetime.strptime to return consistent date objects for testing
    with patch('main.datetime') as mock_datetime:
        mock_date1 = MagicMock()
        mock_date1.strftime.return_value = '20240115'
        
        mock_date2 = MagicMock()
        mock_date2.strftime.return_value = '20240116'
        
        # Return different date objects for different input strings
        def strptime_side_effect(date_str, format_str):
            if date_str == '15-01-2024' or date_str == '15-Jan-2024':
                return mock_date1
            else:
                return mock_date2
        
        mock_datetime.strptime.side_effect = strptime_side_effect
        
        # Call the function
        main.calculate_total_value(sample_csv_data)
    
    # Check output
    output = mock_stdout.getvalue()
    
    # With these mock rates, the calculation should be:
    # 100 shares at $150.50 with rate 145.0 = 2,182,250 JPY
    # 200 shares at $200.25 with rate 147.5 = 5,907,375 JPY
    # Total should be 8,089,625 JPY
    assert "為替レート: ¥145.00" in output
    assert "為替レート: ¥147.50" in output


@patch('sys.stdout', new_callable=StringIO)
@patch('utils.get_exchange_rate')
@patch('utils.convert_date_format')
def test_calculate_total_value_no_exchange_rate(mock_convert_date, mock_get_rate, mock_stdout, sample_csv_data):
    """Test calculate_total_value function when no exchange rate is found."""
    # Setup mocks
    mock_convert_date.side_effect = lambda x: '15-Jan-2024'
    mock_get_rate.return_value = None  # No exchange rate found
    
    # Call the function
    main.calculate_total_value(sample_csv_data)
    
    # Check output
    output = mock_stdout.getvalue()
    
    # Should be empty since without exchange rates, no details are added
    assert "株のVest詳細" in output
    assert "総額: ¥0.00" in output
