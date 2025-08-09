"""Tests for the CalendarGenerator class."""

import pytest
from datetime import datetime
import pytz
from calendar_link import CalendarEvent, CalendarGenerator
from calendar_link.exceptions import UnsupportedCalendarServiceError


class TestCalendarGenerator:
    """Test cases for CalendarGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = CalendarGenerator()
        self.event = CalendarEvent(
            title="Test Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0),
            description="Test description",
            location="Test Location",
            attendees=["john@example.com", "jane@example.com"]
        )

    def test_get_supported_services(self):
        """Test getting list of supported services."""
        services = self.generator.get_supported_services()
        
        expected_services = {
            "google", "apple", "yahoo", "aol", 
            "outlook", "office365", "ics"
        }
        
        assert set(services.keys()) == expected_services
        assert services["google"] == "Google Calendar"
        assert services["apple"] == "Apple Calendar"

    def test_generate_google_link(self):
        """Test generating Google Calendar link."""
        link = self.generator.generate_link(self.event, "google")
        
        assert "calendar.google.com" in link
        assert "action=TEMPLATE" in link
        assert "text=Test+Meeting" in link
        assert "details=Test+description" in link
        assert "location=Test+Location" in link
        assert "add=john%40example.com%2Cjane%40example.com" in link

    def test_generate_apple_link(self):
        """Test generating Apple Calendar link."""
        link = self.generator.generate_link(self.event, "apple")
        
        assert "webcal://calendar.apple.com" in link
        assert "title=Test%20Meeting" in link
        assert "start=2024-01-15T10:00:00" in link
        assert "end=2024-01-15T11:00:00" in link
        assert "description=Test%20description" in link
        assert "location=Test%20Location" in link

    def test_generate_yahoo_link(self):
        """Test generating Yahoo Calendar link."""
        link = self.generator.generate_link(self.event, "yahoo")
        
        assert "calendar.yahoo.com" in link
        assert "v=60" in link
        assert "title=Test+Meeting" in link
        assert "st=20240115T100000Z" in link
        assert "et=20240115T110000Z" in link
        assert "desc=Test+description" in link
        assert "in_loc=Test+Location" in link

    def test_generate_aol_link(self):
        """Test generating AOL Calendar link."""
        link = self.generator.generate_link(self.event, "aol")
        
        assert "calendar.aol.com" in link
        assert "v=60" in link
        assert "title=Test+Meeting" in link
        assert "st=20240115T100000Z" in link
        assert "et=20240115T110000Z" in link
        assert "desc=Test+description" in link
        assert "in_loc=Test+Location" in link

    def test_generate_outlook_link(self):
        """Test generating Microsoft Outlook link."""
        link = self.generator.generate_link(self.event, "outlook")
        
        assert "outlook.live.com" in link
        assert "path=%2Fcalendar%2Faction%2Fcompose" in link
        assert "rru=addevent" in link
        assert "subject=Test+Meeting" in link
        assert "startdt=2024-01-15T10%3A00%3A00" in link
        assert "enddt=2024-01-15T11%3A00%3A00" in link
        assert "body=Test+description" in link
        assert "location=Test+Location" in link

    def test_generate_office365_link(self):
        """Test generating Microsoft 365 link."""
        link = self.generator.generate_link(self.event, "office365")
        
        # Office365 should use the same format as Outlook
        assert "outlook.live.com" in link
        assert "path=%2Fcalendar%2Faction%2Fcompose" in link
        assert "rru=addevent" in link

    def test_generate_ics(self):
        """Test generating ICS file content."""
        ics_content = self.generator.generate_ics(self.event)
        
        assert "BEGIN:VCALENDAR" in ics_content
        assert "END:VCALENDAR" in ics_content
        assert "BEGIN:VEVENT" in ics_content
        assert "END:VEVENT" in ics_content
        assert "SUMMARY:Test Meeting" in ics_content
        assert "DESCRIPTION:Test description" in ics_content
        assert "LOCATION:Test Location" in ics_content

    def test_generate_all_links(self):
        """Test generating all links at once."""
        all_links = self.generator.generate_all_links(self.event)
        
        expected_services = {"google", "apple", "yahoo", "aol", "outlook", "office365", "ics"}
        assert set(all_links.keys()) == expected_services
        
        # Check that all links are generated (not error messages)
        for service, link in all_links.items():
            if service != "ics":
                assert not link.startswith("Error:")
                assert len(link) > 0
            else:
                assert "BEGIN:VCALENDAR" in link

    def test_unsupported_service(self):
        """Test that unsupported service raises error."""
        with pytest.raises(UnsupportedCalendarServiceError, match="Unsupported service: invalid_service"):
            self.generator.generate_link(self.event, "invalid_service")

    def test_case_insensitive_service_names(self):
        """Test that service names are case insensitive."""
        google_link_upper = self.generator.generate_link(self.event, "GOOGLE")
        google_link_lower = self.generator.generate_link(self.event, "google")
        
        assert google_link_upper == google_link_lower

    def test_event_without_description(self):
        """Test generating links for event without description."""
        event = CalendarEvent(
            title="Simple Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0)
        )
        
        link = self.generator.generate_link(event, "google")
        assert "calendar.google.com" in link
        assert "text=Simple+Meeting" in link
        assert "details=" not in link  # No description parameter

    def test_event_without_location(self):
        """Test generating links for event without location."""
        event = CalendarEvent(
            title="Virtual Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0),
            description="Virtual meeting"
        )
        
        link = self.generator.generate_link(event, "google")
        assert "calendar.google.com" in link
        assert "location=" not in link  # No location parameter

    def test_event_without_attendees(self):
        """Test generating links for event without attendees."""
        event = CalendarEvent(
            title="Solo Meeting",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0)
        )
        
        link = self.generator.generate_link(event, "google")
        assert "calendar.google.com" in link
        assert "add=" not in link  # No attendees parameter

    def test_all_day_event_links(self):
        """Test generating links for all-day events."""
        event = CalendarEvent(
            title="Vacation Day",
            start_time=datetime(2024, 1, 15, 0, 0),
            end_time=datetime(2024, 1, 15, 0, 0),
            all_day=True
        )
        
        # Test Google Calendar link for all-day event
        link = self.generator.generate_link(event, "google")
        assert "calendar.google.com" in link
        assert "text=Vacation+Day" in link

    def test_timezone_aware_event(self):
        """Test generating links for timezone-aware events."""
        ny_tz = pytz.timezone("America/New_York")
        start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))
        end_time = ny_tz.localize(datetime(2024, 1, 15, 11, 0))
        
        event = CalendarEvent(
            title="Timezone Meeting",
            start_time=start_time,
            end_time=end_time,
            timezone="America/New_York"
        )
        
        link = self.generator.generate_link(event, "google")
        assert "calendar.google.com" in link
        assert "text=Timezone+Meeting" in link

    def test_ics_with_attendees(self):
        """Test ICS generation with attendees."""
        ics_content = self.generator.generate_ics(self.event)
        
        # Check that attendees are included in ICS
        assert "ATTENDEE:john@example.com" in ics_content
        assert "ATTENDEE:jane@example.com" in ics_content

    def test_ics_without_optional_fields(self):
        """Test ICS generation without optional fields."""
        event = CalendarEvent(
            title="Simple Event",
            start_time=datetime(2024, 1, 15, 10, 0),
            end_time=datetime(2024, 1, 15, 11, 0)
        )
        
        ics_content = self.generator.generate_ics(event)
        
        assert "BEGIN:VCALENDAR" in ics_content
        assert "BEGIN:VEVENT" in ics_content
        assert "SUMMARY:Simple Event" in ics_content
        assert "DESCRIPTION:" not in ics_content  # No description
        assert "LOCATION:" not in ics_content  # No location
        assert "ATTENDEE:" not in ics_content  # No attendees 