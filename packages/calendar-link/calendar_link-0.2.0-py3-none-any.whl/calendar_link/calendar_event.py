"""Calendar event representation and validation."""

from datetime import datetime, timedelta
from typing import Optional, List
import pytz
from dateutil import parser

from .exceptions import InvalidEventDataError, TimezoneError


class CalendarEvent:
    """Represents a calendar event with all necessary information for generating links and ICS files."""

    def __init__(
        self,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        all_day: bool = False,
        timezone: Optional[str] = None,
    ):
        """
        Initialize a calendar event.

        Args:
            title: Event title/summary
            start_time: Event start time (datetime object)
            end_time: Event end time (datetime object). If None, defaults to start_time + 1 hour
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            all_day: Whether this is an all-day event
            timezone: Timezone string (e.g., 'America/New_York'). If None, uses start_time's timezone
        """
        self.title = title
        self.start_time = start_time
        self.end_time = end_time or (start_time + timedelta(hours=1))
        self.description = description
        self.location = location
        self.attendees = attendees or []
        self.all_day = all_day
        self.timezone = timezone or self._get_timezone_from_datetime(start_time)

        self._validate_event()

    def _get_timezone_from_datetime(self, dt: datetime) -> str:
        """Extract timezone from datetime object."""
        if dt.tzinfo is None:
            return "UTC"
        return str(dt.tzinfo)

    def _validate_event(self) -> None:
        """Validate event data."""
        if not self.title or not self.title.strip():
            raise InvalidEventDataError("Event title is required")

        # For all-day events, allow same start and end time
        if not self.all_day and self.start_time >= self.end_time:
            raise InvalidEventDataError("Start time must be before end time")

        if self.all_day and (self.start_time.hour != 0 or self.end_time.hour != 0):
            raise InvalidEventDataError("All-day events should have 00:00 as time")

    @classmethod
    def from_dict(cls, data: dict) -> "CalendarEvent":
        """
        Create a CalendarEvent from a dictionary.

        Args:
            data: Dictionary containing event data

        Returns:
            CalendarEvent instance

        Example:
            event = CalendarEvent.from_dict({
                'title': 'Meeting',
                'start_time': '2024-01-15T10:00:00',
                'end_time': '2024-01-15T11:00:00',
                'description': 'Team meeting',
                'location': 'Conference Room A'
            })
        """
        # Parse datetime strings if provided
        start_time = data.get("start_time")
        if isinstance(start_time, str):
            start_time = parser.parse(start_time)

        end_time = data.get("end_time")
        if isinstance(end_time, str):
            end_time = parser.parse(end_time)

        return cls(
            title=data["title"],
            start_time=start_time,
            end_time=end_time,
            description=data.get("description"),
            location=data.get("location"),
            attendees=data.get("attendees", []),
            all_day=data.get("all_day", False),
            timezone=data.get("timezone"),
        )

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "description": self.description,
            "location": self.location,
            "attendees": self.attendees,
            "all_day": self.all_day,
            "timezone": self.timezone,
        }

    def get_duration_minutes(self) -> int:
        """Get event duration in minutes."""
        duration = self.end_time - self.start_time
        return int(duration.total_seconds() / 60)

    def is_same_day(self) -> bool:
        """Check if start and end time are on the same day."""
        return self.start_time.date() == self.end_time.date()

    def __repr__(self) -> str:
        return f"CalendarEvent(title='{self.title}', start_time={self.start_time}, end_time={self.end_time})" 