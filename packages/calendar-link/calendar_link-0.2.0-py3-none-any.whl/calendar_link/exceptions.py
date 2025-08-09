"""Custom exceptions for the calendar link package."""


class CalendarLinkError(Exception):
    """Base exception for calendar link errors."""
    pass


class InvalidEventDataError(CalendarLinkError):
    """Raised when event data is invalid or missing required fields."""
    pass


class UnsupportedCalendarServiceError(CalendarLinkError):
    """Raised when an unsupported calendar service is requested."""
    pass


class TimezoneError(CalendarLinkError):
    """Raised when there's an issue with timezone handling."""
    pass 