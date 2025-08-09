"""Utility functions for calendar operations."""

import re
from datetime import datetime, timedelta
from typing import Optional, Union
import pytz
from dateutil import parser, tz


def parse_datetime(
    date_string: str, 
    timezone: Optional[str] = None,
    default_timezone: str = "UTC"
) -> datetime:
    """
    Parse a datetime string with timezone support.
    
    Args:
        date_string: Date/time string to parse
        timezone: Timezone to apply (e.g., 'America/New_York')
        default_timezone: Default timezone if none specified
        
    Returns:
        datetime object with timezone info
        
    Examples:
        >>> parse_datetime("2024-01-15 10:00:00", "America/New_York")
        datetime.datetime(2024, 1, 15, 10, 0, tzinfo=<DstTzInfo 'America/New_York' EST-1 day, 19:00:00 STD>)
    """
    try:
        dt = parser.parse(date_string)
        
        # If no timezone info, apply the specified timezone
        if dt.tzinfo is None:
            if timezone:
                tz_obj = pytz.timezone(timezone)
                dt = tz_obj.localize(dt)
            else:
                tz_obj = pytz.timezone(default_timezone)
                dt = tz_obj.localize(dt)
        
        return dt
    except Exception as e:
        raise ValueError(f"Could not parse datetime string '{date_string}': {str(e)}")


def format_datetime_for_service(
    dt: datetime, 
    service: str,
    timezone: Optional[str] = None
) -> str:
    """
    Format datetime for specific calendar service.
    
    Args:
        dt: datetime object
        service: Calendar service name
        timezone: Optional timezone override
        
    Returns:
        Formatted datetime string
    """
    if timezone:
        tz_obj = pytz.timezone(timezone)
        dt = dt.astimezone(tz_obj)
    
    if service.lower() in ["google", "yahoo", "aol"]:
        return dt.strftime("%Y%m%dT%H%M%SZ")
    elif service.lower() in ["outlook", "office365"]:
        return dt.isoformat()
    elif service.lower() == "apple":
        return dt.isoformat()
    else:
        return dt.isoformat()


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Additional checks for common invalid patterns
    if not email or '@' not in email:
        return False
    if email.startswith('@') or email.endswith('@'):
        return False
    if '..' in email.split('@')[0] or '..' in email.split('@')[1]:
        return False
    if email.count('@') != 1:
        return False
    return bool(re.match(pattern, email))


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize text for calendar services.
    
    Args:
        text: Text to sanitize
        max_length: Maximum length allowed
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove or replace problematic characters
    sanitized = text.replace("\n", " ").replace("\r", " ")
    sanitized = re.sub(r'\s+', ' ', sanitized)  # Replace multiple spaces with single space
    sanitized = sanitized.strip()
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized


def get_timezone_offset(timezone: str) -> int:
    """
    Get timezone offset in minutes from UTC.
    
    Args:
        timezone: Timezone name (e.g., 'America/New_York')
        
    Returns:
        Offset in minutes from UTC
    """
    try:
        tz_obj = pytz.timezone(timezone)
        now = datetime.now(tz_obj)
        offset = now.utcoffset()
        return int(offset.total_seconds() / 60) if offset else 0
    except pytz.exceptions.UnknownTimeZoneError:
        return 0


def is_business_hours(dt: datetime, timezone: str = "UTC") -> bool:
    """
    Check if datetime is during business hours (9 AM - 5 PM, Monday-Friday).
    
    Args:
        dt: datetime object
        timezone: Timezone to check against
        
    Returns:
        True if during business hours, False otherwise
    """
    try:
        tz_obj = pytz.timezone(timezone)
        local_dt = dt.astimezone(tz_obj)
        hour = local_dt.hour
        weekday = local_dt.weekday()  # Monday = 0, Sunday = 6
        return weekday < 5 and 9 <= hour < 17  # Monday-Friday, 9 AM - 5 PM
    except pytz.exceptions.UnknownTimeZoneError:
        return False


def get_next_business_day(dt: datetime, timezone: str = "UTC") -> datetime:
    """
    Get the next business day (Monday-Friday).
    
    Args:
        dt: Starting datetime
        timezone: Timezone to use
        
    Returns:
        Next business day datetime
    """
    current = dt
    while True:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Monday = 0, Friday = 4
            return current


def format_duration(minutes: int) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string
    """
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} hours"
        else:
            return f"{hours} hours {remaining_minutes} minutes"
    else:
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return f"{days} days"
        else:
            return f"{days} days {remaining_hours} hours" 