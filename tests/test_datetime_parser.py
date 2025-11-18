"""
Unit tests for datetime_parser module
"""

import unittest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime_parser import (
    parse_date, parse_time, parse_datetime,
    validate_datetime, format_datetime, extract_datetime_from_text
)

class TestDateTimeParser(unittest.TestCase):
    """Test cases for datetime parsing functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def test_parse_date_today(self):
        """Test parsing 'today'."""
        result = parse_date('today')
        self.assertEqual(result, self.today)
    
    def test_parse_date_tomorrow(self):
        """Test parsing 'tomorrow'."""
        result = parse_date('tomorrow')
        expected = self.today + timedelta(days=1)
        self.assertEqual(result, expected)
    
    def test_parse_date_yesterday(self):
        """Test parsing 'yesterday'."""
        result = parse_date('yesterday')
        expected = self.today - timedelta(days=1)
        self.assertEqual(result, expected)
    
    def test_parse_date_next_week(self):
        """Test parsing 'next week'."""
        result = parse_date('next week')
        expected = self.today + timedelta(weeks=1)
        self.assertEqual(result, expected)
    
    def test_parse_time_12hr(self):
        """Test parsing 12-hour time format."""
        result = parse_time('3pm')
        self.assertEqual(result, (15, 0))
    
    def test_parse_time_24hr(self):
        """Test parsing 24-hour time format."""
        result = parse_time('15:30')
        self.assertEqual(result, (15, 30))
    
    def test_parse_time_am(self):
        """Test parsing AM time."""
        result = parse_time('9am')
        self.assertEqual(result, (9, 0))
    
    def test_parse_datetime_combined(self):
        """Test parsing combined date and time."""
        date_str = 'tomorrow'
        time_str = '3pm'
        result = parse_datetime(date_str, time_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.hour, 15)
        self.assertEqual(result.minute, 0)
    
    def test_validate_datetime_future(self):
        """Test validating future datetime."""
        future_dt = datetime.now() + timedelta(days=1)
        self.assertTrue(validate_datetime(future_dt))
    
    def test_validate_datetime_past(self):
        """Test validating past datetime."""
        past_dt = datetime.now() - timedelta(days=1)
        self.assertFalse(validate_datetime(past_dt))
    
    def test_format_datetime(self):
        """Test formatting datetime."""
        dt = datetime(2024, 3, 15, 14, 30)
        formatted = format_datetime(dt)
        self.assertIn('March', formatted)
        self.assertIn('15', formatted)
        self.assertIn('2024', formatted)
    
    def test_extract_datetime_from_text(self):
        """Test extracting datetime from natural language."""
        text = "Remind me tomorrow at 3pm"
        result = extract_datetime_from_text(text)
        self.assertIsNotNone(result)
        # Should extract date and time
        self.assertIsNotNone(result.get('date') or result.get('time'))

if __name__ == '__main__':
    unittest.main()

