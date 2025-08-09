"""Tests for utility functions."""

import pytest
from datetime import datetime, timedelta
import pytz
from calendar_link.utils import (
    parse_datetime,
    format_datetime_for_service,
    validate_email,
    sanitize_text,
    get_timezone_offset,
    is_business_hours,
    get_next_business_day,
    format_duration
)


class TestUtils:
    """Test cases for utility functions."""

    def test_parse_datetime_with_timezone(self):
        """Test parsing datetime with timezone."""
        dt = parse_datetime("2024-01-15 14:30:00", "America/New_York")
        
        assert isinstance(dt, datetime)
        assert dt.tzinfo is not None
        assert "America/New_York" in str(dt.tzinfo)

    def test_parse_datetime_without_timezone(self):
        """Test parsing datetime without timezone."""
        dt = parse_datetime("2024-01-15 14:30:00")
        
        assert isinstance(dt, datetime)
        assert dt.tzinfo is not None
        assert "UTC" in str(dt.tzinfo)

    def test_parse_datetime_invalid_string(self):
        """Test parsing invalid datetime string."""
        with pytest.raises(ValueError, match="Could not parse datetime string"):
            parse_datetime("invalid datetime")

    def test_format_datetime_for_service_google(self):
        """Test formatting datetime for Google Calendar."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "google")
        
        assert formatted == "20240115T143000Z"

    def test_format_datetime_for_service_outlook(self):
        """Test formatting datetime for Outlook."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "outlook")
        
        assert formatted == "2024-01-15T14:30:00"

    def test_format_datetime_for_service_with_timezone(self):
        """Test formatting datetime with timezone override."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "google", "America/New_York")
        
        # Should be different due to timezone conversion
        assert formatted != "20240115T143000Z"

    def test_validate_email_valid(self):
        """Test validating valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test validating invalid email addresses."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "user@example..com"
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False

    def test_sanitize_text_basic(self):
        """Test basic text sanitization."""
        dirty_text = "Event\nDescription\nwith\nnewlines"
        clean_text = sanitize_text(dirty_text)
        
        assert clean_text == "Event Description with newlines"

    def test_sanitize_text_extra_spaces(self):
        """Test sanitizing text with extra spaces."""
        dirty_text = "Event    with    extra    spaces"
        clean_text = sanitize_text(dirty_text)
        
        assert clean_text == "Event with extra spaces"

    def test_sanitize_text_truncation(self):
        """Test text truncation when too long."""
        long_text = "A" * 1001
        clean_text = sanitize_text(long_text, max_length=1000)
        
        assert len(clean_text) == 1000
        assert clean_text.endswith("...")

    def test_sanitize_text_empty(self):
        """Test sanitizing empty text."""
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""

    def test_get_timezone_offset(self):
        """Test getting timezone offset."""
        offset = get_timezone_offset("America/New_York")
        
        # Should be a reasonable offset (between -12 and +14 hours)
        assert -720 <= offset <= 840

    def test_get_timezone_offset_invalid(self):
        """Test getting offset for invalid timezone."""
        offset = get_timezone_offset("Invalid/Timezone")
        
        assert offset == 0

    def test_is_business_hours_true(self):
        """Test checking business hours during work day."""
        # 2 PM on a weekday
        dt = datetime(2024, 1, 15, 14, 0, 0)  # Monday
        assert is_business_hours(dt, "UTC") is True

    def test_is_business_hours_false(self):
        """Test checking business hours outside work day."""
        # 8 PM on a weekday
        dt = datetime(2024, 1, 15, 20, 0, 0)  # Monday
        assert is_business_hours(dt, "UTC") is False

    def test_is_business_hours_weekend(self):
        """Test checking business hours on weekend."""
        # Saturday
        dt = datetime(2024, 1, 20, 14, 0, 0)  # Saturday
        assert is_business_hours(dt, "UTC") is False

    def test_get_next_business_day(self):
        """Test getting next business day."""
        # Friday
        current = datetime(2024, 1, 19, 10, 0, 0)  # Friday
        next_business = get_next_business_day(current)
        
        # Should be Monday
        assert next_business.weekday() == 0  # Monday
        assert next_business.date() == datetime(2024, 1, 22).date()

    def test_get_next_business_day_from_weekend(self):
        """Test getting next business day from weekend."""
        # Saturday
        current = datetime(2024, 1, 20, 10, 0, 0)  # Saturday
        next_business = get_next_business_day(current)
        
        # Should be Monday
        assert next_business.weekday() == 0  # Monday
        assert next_business.date() == datetime(2024, 1, 22).date()

    def test_format_duration_minutes(self):
        """Test formatting duration in minutes."""
        assert format_duration(30) == "30 minutes"
        assert format_duration(45) == "45 minutes"

    def test_format_duration_hours(self):
        """Test formatting duration in hours."""
        assert format_duration(60) == "1 hours"
        assert format_duration(90) == "1 hours 30 minutes"
        assert format_duration(120) == "2 hours"

    def test_format_duration_days(self):
        """Test formatting duration in days."""
        assert format_duration(1440) == "1 days"  # 24 hours
        assert format_duration(2880) == "2 days"  # 48 hours
        assert format_duration(1500) == "1 days 1 hours"  # 25 hours

    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        assert format_duration(0) == "0 minutes"

    def test_format_datetime_for_service_apple(self):
        """Test formatting datetime for Apple Calendar."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "apple")
        
        assert formatted == "2024-01-15T14:30:00"

    def test_format_datetime_for_service_yahoo(self):
        """Test formatting datetime for Yahoo Calendar."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "yahoo")
        
        assert formatted == "20240115T143000Z"

    def test_format_datetime_for_service_aol(self):
        """Test formatting datetime for AOL Calendar."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "aol")
        
        assert formatted == "20240115T143000Z"

    def test_format_datetime_for_service_unknown(self):
        """Test formatting datetime for unknown service."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        formatted = format_datetime_for_service(dt, "unknown")
        
        assert formatted == "2024-01-15T14:30:00" 