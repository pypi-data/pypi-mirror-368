"""Tests for custom exceptions."""

import pytest
from calendar_link.exceptions import (
    CalendarLinkError,
    InvalidEventDataError,
    UnsupportedCalendarServiceError,
    TimezoneError
)


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_calendar_link_error_inheritance(self):
        """Test that CalendarLinkError inherits from Exception."""
        error = CalendarLinkError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_invalid_event_data_error_inheritance(self):
        """Test that InvalidEventDataError inherits from CalendarLinkError."""
        error = InvalidEventDataError("Invalid event data")
        assert isinstance(error, CalendarLinkError)
        assert isinstance(error, Exception)
        assert str(error) == "Invalid event data"

    def test_unsupported_calendar_service_error_inheritance(self):
        """Test that UnsupportedCalendarServiceError inherits from CalendarLinkError."""
        error = UnsupportedCalendarServiceError("Unsupported service")
        assert isinstance(error, CalendarLinkError)
        assert isinstance(error, Exception)
        assert str(error) == "Unsupported service"

    def test_timezone_error_inheritance(self):
        """Test that TimezoneError inherits from CalendarLinkError."""
        error = TimezoneError("Timezone error")
        assert isinstance(error, CalendarLinkError)
        assert isinstance(error, Exception)
        assert str(error) == "Timezone error"

    def test_exception_attributes(self):
        """Test that exceptions have proper attributes."""
        error = InvalidEventDataError("Test message")
        assert hasattr(error, '__str__')
        assert hasattr(error, '__repr__')

    def test_exception_equality(self):
        """Test exception equality."""
        error1 = InvalidEventDataError("Same message")
        error2 = InvalidEventDataError("Same message")
        error3 = InvalidEventDataError("Different message")
        
        # Exceptions with same message should be equal
        assert str(error1) == str(error2)
        assert str(error1) != str(error3)

    def test_exception_types(self):
        """Test that different exception types are distinct."""
        calendar_error = CalendarLinkError("Base error")
        invalid_error = InvalidEventDataError("Invalid data")
        unsupported_error = UnsupportedCalendarServiceError("Unsupported")
        timezone_error = TimezoneError("Timezone issue")
        
        # All should be different types
        assert type(calendar_error) != type(invalid_error)
        assert type(invalid_error) != type(unsupported_error)
        assert type(unsupported_error) != type(timezone_error)
        
        # But all should be CalendarLinkError
        assert isinstance(calendar_error, CalendarLinkError)
        assert isinstance(invalid_error, CalendarLinkError)
        assert isinstance(unsupported_error, CalendarLinkError)
        assert isinstance(timezone_error, CalendarLinkError) 