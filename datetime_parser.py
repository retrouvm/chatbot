"""
Date and time parsing utilities for RemindMe! Chatbot
Uses python-dateutil for robust date/time parsing
"""

from datetime import datetime, timedelta
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
import re
import config
from logger import setup_logger

logger = setup_logger('datetime_parser')

def parse_date(date_string):
    """
    Parse a date string into a datetime object.
    Handles relative dates like 'today', 'tomorrow', 'next week', etc.
    
    Args:
        date_string: String containing date information
    
    Returns:
        datetime object or None if parsing fails
    """
    if not date_string or not date_string.strip():
        return None
    
    date_string = date_string.strip().lower()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Handle relative date keywords
    relative_keywords = config.DATETIME_CONFIG['relative_date_keywords']
    
    if date_string == 'today':
        return today
    elif date_string == 'tomorrow':
        return today + timedelta(days=1)
    elif date_string == 'yesterday':
        return today - timedelta(days=1)
    elif 'next week' in date_string:
        return today + timedelta(weeks=1)
    elif 'next month' in date_string:
        return today + relativedelta(months=1)
    elif 'next year' in date_string:
        return today + relativedelta(years=1)
    elif 'last week' in date_string:
        return today - timedelta(weeks=1)
    elif 'last month' in date_string:
        return today - relativedelta(months=1)
    
    # Try parsing with dateutil
    try:
        if config.DATETIME_CONFIG['use_dateutil']:
            parsed_date = date_parser.parse(date_string, default=today)
            # If no time component, set to start of day
            if parsed_date.hour == 0 and parsed_date.minute == 0 and parsed_date.second == 0:
                # Check if original string had time info
                if not re.search(r'\d{1,2}:\d{2}', date_string):
                    parsed_date = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
            return parsed_date
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse date '{date_string}': {e}")
        return None
    
    return None

def parse_time(time_string):
    """
    Parse a time string into time components.
    
    Args:
        time_string: String containing time information (e.g., "3pm", "15:30", "9:00 AM")
    
    Returns:
        tuple: (hour, minute) or None if parsing fails
    """
    if not time_string or not time_string.strip():
        return None
    
    time_string = time_string.strip().lower()
    
    # Remove common prefixes
    time_string = re.sub(r'^at\s+', '', time_string)
    time_string = re.sub(r'^@\s*', '', time_string)
    
    # Try parsing with dateutil
    try:
        if config.DATETIME_CONFIG['use_dateutil']:
            # Create a datetime with today's date and parse time
            today = datetime.now()
            parsed_datetime = date_parser.parse(time_string, default=today)
            return (parsed_datetime.hour, parsed_datetime.minute)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse time '{time_string}': {e}")
    
    # Fallback: try regex patterns
    # Pattern for "3pm", "3 PM", "15:30", etc.
    patterns = [
        (r'(\d{1,2}):(\d{2})\s*(am|pm)?', lambda m: (int(m.group(1)) % 12 + (12 if m.group(3) == 'pm' else 0), int(m.group(2)))),
        (r'(\d{1,2})\s*(am|pm)', lambda m: (int(m.group(1)) % 12 + (12 if m.group(2) == 'pm' else 0), 0)),
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, time_string, re.IGNORECASE)
        if match:
            try:
                return converter(match)
            except (ValueError, IndexError):
                continue
    
    return None

def parse_datetime(date_string, time_string=None):
    """
    Parse both date and time strings into a single datetime object.
    
    Args:
        date_string: String containing date information
        time_string: Optional string containing time information
    
    Returns:
        datetime object or None if parsing fails
    """
    date_obj = parse_date(date_string)
    if date_obj is None:
        return None
    
    if time_string:
        time_tuple = parse_time(time_string)
        if time_tuple:
            hour, minute = time_tuple
            date_obj = date_obj.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return date_obj

def validate_datetime(dt):
    """
    Validate that a datetime is in the future (for reminders/events).
    
    Args:
        dt: datetime object to validate
    
    Returns:
        bool: True if datetime is valid and in the future
    """
    if dt is None:
        return False
    
    now = datetime.now()
    return dt > now

def format_datetime(dt, include_time=True):
    """
    Format datetime object into a readable string.
    
    Args:
        dt: datetime object
        include_time: Whether to include time in the format
    
    Returns:
        Formatted string
    """
    if dt is None:
        return "Invalid date/time"
    
    if include_time:
        return dt.strftime("%B %d, %Y at %I:%M %p")
    else:
        return dt.strftime("%B %d, %Y")

def extract_datetime_from_text(text):
    """
    Extract date and time information from natural language text.
    
    Args:
        text: Natural language text containing date/time information
    
    Returns:
        dict: Contains 'date', 'time', 'datetime' keys with parsed values
    """
    result = {
        'date': None,
        'time': None,
        'datetime': None
    }
    
    # Try to find date and time patterns in text
    # This is a simple implementation - could be enhanced with more sophisticated NLP
    date_patterns = [
        r'\b(today|tomorrow|yesterday|next week|next month)\b',
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?',
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    ]
    
    time_patterns = [
        r'\b\d{1,2}:\d{2}\s*(am|pm)\b',
        r'\b\d{1,2}\s*(am|pm)\b',
        r'\b\d{1,2}:\d{2}\b',
    ]
    
    # Extract date
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result['date'] = parse_date(match.group(0))
            break
    
    # Extract time
    for pattern in time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            time_tuple = parse_time(match.group(0))
            if time_tuple:
                result['time'] = time_tuple
            break
    
    # Combine if both found
    if result['date'] and result['time']:
        hour, minute = result['time']
        result['datetime'] = result['date'].replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return result

