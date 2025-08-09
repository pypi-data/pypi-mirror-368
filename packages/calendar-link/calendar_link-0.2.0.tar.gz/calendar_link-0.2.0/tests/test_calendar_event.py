"""Tests for the CalendarEvent class."""

import pytest
from datetime import datetime, timedelta
import pytz
from calendar_link import CalendarEvent
from calendar_link.exceptions import InvalidEventDataError


class TestCalendarEvent:
    """Test cases for CalendarEvent class."""

    def test_create_basic_event(self):
        """Test creating a basic calendar event."""
        start_time = datetime(2024, 1, 15, 10, 0)
        event = CalendarEvent(
            title="Test Meeting",
            start_time=start_time,
            description="Test description",
            location="Test Location"
        )
        
        assert event.title == "Test Meeting"
        assert event.start_time == start_time
        assert event.end_time == start_time + timedelta(hours=1)
        assert event.description == "Test description"
        assert event.location == "Test Location"
        assert event.attendees == []
        assert event.all_day is False

    def test_create_event_with_end_time(self):
        """Test creating an event with explicit end time."""
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 30)
        event = CalendarEvent(
            title="Test Meeting",
            start_time=start_time,
            end_time=end_time
        )
        
        assert event.end_time == end_time
        assert event.get_duration_minutes() == 90

    def test_create_event_with_attendees(self):
        """Test creating an event with attendees."""
        event = CalendarEvent(
            title="Team Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            attendees=["john@example.com", "jane@example.com"]
        )
        
        assert len(event.attendees) == 2
        assert "john@example.com" in event.attendees
        assert "jane@example.com" in event.attendees

    def test_create_all_day_event(self):
        """Test creating an all-day event."""
        event = CalendarEvent(
            title="Vacation Day",
            start_time=datetime(2024, 1, 15, 0, 0),
            end_time=datetime(2024, 1, 15, 0, 0),
            all_day=True
        )
        
        assert event.all_day is True
        assert event.start_time.hour == 0
        assert event.end_time.hour == 0

    def test_create_event_with_timezone(self):
        """Test creating an event with timezone."""
        ny_tz = pytz.timezone("America/New_York")
        start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))
        
        event = CalendarEvent(
            title="Meeting",
            start_time=start_time,
            timezone="America/New_York"
        )
        
        assert event.timezone == "America/New_York"

    def test_invalid_empty_title(self):
        """Test that empty title raises error."""
        with pytest.raises(InvalidEventDataError, match="Event title is required"):
            CalendarEvent(
                title="",
                start_time=datetime(2024, 1, 15, 10, 0)
            )

    def test_invalid_whitespace_title(self):
        """Test that whitespace-only title raises error."""
        with pytest.raises(InvalidEventDataError, match="Event title is required"):
            CalendarEvent(
                title="   ",
                start_time=datetime(2024, 1, 15, 10, 0)
            )

    def test_invalid_end_before_start(self):
        """Test that end time before start time raises error."""
        with pytest.raises(InvalidEventDataError, match="Start time must be before end time"):
            CalendarEvent(
                title="Test Meeting",
                start_time=datetime(2024, 1, 15, 11, 0),
                end_time=datetime(2024, 1, 15, 10, 0)
            )

    def test_invalid_all_day_event_with_time(self):
        """Test that all-day events with non-zero hours raise error."""
        with pytest.raises(InvalidEventDataError, match="All-day events should have 00:00 as time"):
            CalendarEvent(
                title="Test Meeting",
                start_time=datetime(2024, 1, 15, 10, 0),
                end_time=datetime(2024, 1, 15, 11, 0),
                all_day=True
            )

    def test_from_dict_with_datetime_strings(self):
        """Test creating event from dictionary with datetime strings."""
        event_data = {
            "title": "Test Meeting",
            "start_time": "2024-01-15T10:00:00",
            "end_time": "2024-01-15T11:00:00",
            "description": "Test description",
            "location": "Test Location",
            "attendees": ["john@example.com"],
            "all_day": False
        }
        
        event = CalendarEvent.from_dict(event_data)
        
        assert event.title == "Test Meeting"
        assert event.start_time == datetime(2024, 1, 15, 10, 0)
        assert event.end_time == datetime(2024, 1, 15, 11, 0)
        assert event.description == "Test description"
        assert event.location == "Test Location"
        assert event.attendees == ["john@example.com"]
        assert event.all_day is False

    def test_from_dict_with_datetime_objects(self):
        """Test creating event from dictionary with datetime objects."""
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        event_data = {
            "title": "Test Meeting",
            "start_time": start_time,
            "end_time": end_time
        }
        
        event = CalendarEvent.from_dict(event_data)
        
        assert event.start_time == start_time
        assert event.end_time == end_time

    def test_to_dict(self):
        """Test converting event to dictionary."""
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)
        
        event = CalendarEvent(
            title="Test Meeting",
            start_time=start_time,
            end_time=end_time,
            description="Test description",
            location="Test Location",
            attendees=["john@example.com"],
            all_day=False,
            timezone="UTC"
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["title"] == "Test Meeting"
        assert event_dict["start_time"] == start_time.isoformat()
        assert event_dict["end_time"] == end_time.isoformat()
        assert event_dict["description"] == "Test description"
        assert event_dict["location"] == "Test Location"
        assert event_dict["attendees"] == ["john@example.com"]
        assert event_dict["all_day"] is False
        assert event_dict["timezone"] == "UTC"

    def test_get_duration_minutes(self):
        """Test getting event duration in minutes."""
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 30)
        
        event = CalendarEvent(
            title="Test Meeting",
            start_time=start_time,
            end_time=end_time
        )
        
        assert event.get_duration_minutes() == 90

    def test_is_same_day_true(self):
        """Test is_same_day returns True for same day events."""
        event = CalendarEvent(
            title="Test Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0)
        )
        
        assert event.is_same_day() is True

    def test_is_same_day_false(self):
        """Test is_same_day returns False for multi-day events."""
        event = CalendarEvent(
            title="Test Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 16, 10, 0)
        )
        
        assert event.is_same_day() is False

    def test_repr(self):
        """Test string representation of event."""
        event = CalendarEvent(
            title="Test Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0)
        )
        
        repr_str = repr(event)
        assert "CalendarEvent" in repr_str
        assert "Test Meeting" in repr_str
        assert "2024-01-15 10:00:00" in repr_str
        assert "2024-01-15 11:00:00" in repr_str 