"""Calendar link and ICS file generator for various calendar services."""

import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any
from ical.calendar import Calendar
from ical.event import Event as IcalEvent
import pytz

from .calendar_event import CalendarEvent
from .exceptions import UnsupportedCalendarServiceError


class CalendarGenerator:
    """Generate calendar links and ICS files for various calendar services."""

    SUPPORTED_SERVICES = {
        "google": "Google Calendar",
        "apple": "Apple Calendar",
        "yahoo": "Yahoo Calendar",
        "aol": "AOL Calendar",
        "outlook": "Microsoft Outlook",
        "office365": "Microsoft 365",
        "ics": "ICS File",
    }

    def __init__(self):
        """Initialize the calendar generator."""
        pass

    def generate_link(self, event: CalendarEvent, service: str) -> str:
        """
        Generate a calendar link for the specified service.

        Args:
            event: CalendarEvent instance
            service: Calendar service name (google, apple, yahoo, aol, outlook, office365)

        Returns:
            URL string for the calendar service

        Raises:
            UnsupportedCalendarServiceError: If service is not supported
        """
        service = service.lower()
        if service not in self.SUPPORTED_SERVICES:
            raise UnsupportedCalendarServiceError(
                f"Unsupported service: {service}. Supported services: {list(self.SUPPORTED_SERVICES.keys())}"
            )

        if service == "google":
            return self._generate_google_link(event)
        elif service == "apple":
            return self._generate_apple_link(event)
        elif service == "yahoo":
            return self._generate_yahoo_link(event)
        elif service == "aol":
            return self._generate_aol_link(event)
        elif service == "outlook":
            return self._generate_outlook_link(event)
        elif service == "office365":
            return self._generate_office365_link(event)
        else:
            raise UnsupportedCalendarServiceError(f"Service {service} not implemented")

    def generate_ics(self, event: CalendarEvent) -> str:
        """
        Generate ICS file content for the event.

        Args:
            event: CalendarEvent instance

        Returns:
            ICS file content as string
        """
        # Generate ICS content manually
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Calendar Link Generator//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:{event.title.replace(' ', '_')}_{event.start_time.strftime('%Y%m%d%H%M%S')}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{event.start_time.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{event.end_time.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{event.title}",
        ]
        
        if event.description:
            lines.append(f"DESCRIPTION:{event.description}")
        
        if event.location:
            lines.append(f"LOCATION:{event.location}")
        
        # Add attendees
        for attendee in event.attendees:
            lines.append(f"ATTENDEE:{attendee}")
        
        lines.extend([
            "END:VEVENT",
            "END:VCALENDAR"
        ])
        
        return "\r\n".join(lines)

    def generate_all_links(self, event: CalendarEvent) -> Dict[str, str]:
        """
        Generate links for all supported services.

        Args:
            event: CalendarEvent instance

        Returns:
            Dictionary mapping service names to their URLs
        """
        links = {}
        for service in self.SUPPORTED_SERVICES.keys():
            if service != "ics":
                try:
                    links[service] = self.generate_link(event, service)
                except Exception as e:
                    links[service] = f"Error: {str(e)}"

        # Add ICS content
        links["ics"] = self.generate_ics(event)
        return links

    def _generate_google_link(self, event: CalendarEvent) -> str:
        """Generate Google Calendar link."""
        params = {
            "action": "TEMPLATE",
            "text": event.title,
            "dates": self._format_google_dates(event),
        }

        if event.description:
            params["details"] = event.description

        if event.location:
            params["location"] = event.location

        # Add attendees
        if event.attendees:
            params["add"] = ",".join(event.attendees)

        return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"

    def _generate_apple_link(self, event: CalendarEvent) -> str:
        """Generate Apple Calendar link."""
        # Apple Calendar uses a custom URL scheme
        params = {
            "title": event.title,
            "start": event.start_time.isoformat(),
            "end": event.end_time.isoformat(),
        }

        if event.description:
            params["description"] = event.description

        if event.location:
            params["location"] = event.location

        # Apple Calendar URL scheme
        url_parts = [f"title={urllib.parse.quote(event.title)}"]
        url_parts.append(f"start={event.start_time.isoformat()}")
        url_parts.append(f"end={event.end_time.isoformat()}")

        if event.description:
            url_parts.append(f"description={urllib.parse.quote(event.description)}")

        if event.location:
            url_parts.append(f"location={urllib.parse.quote(event.location)}")

        return f"webcal://calendar.apple.com/event?{'&'.join(url_parts)}"

    def _generate_yahoo_link(self, event: CalendarEvent) -> str:
        """Generate Yahoo Calendar link."""
        params = {
            "v": 60,
            "title": event.title,
            "st": self._format_yahoo_datetime(event.start_time),
            "et": self._format_yahoo_datetime(event.end_time),
        }

        if event.description:
            params["desc"] = event.description

        if event.location:
            params["in_loc"] = event.location

        return f"https://calendar.yahoo.com/?{urllib.parse.urlencode(params)}"

    def _generate_aol_link(self, event: CalendarEvent) -> str:
        """Generate AOL Calendar link."""
        # AOL Calendar uses similar format to Yahoo
        params = {
            "v": 60,
            "title": event.title,
            "st": self._format_yahoo_datetime(event.start_time),
            "et": self._format_yahoo_datetime(event.end_time),
        }

        if event.description:
            params["desc"] = event.description

        if event.location:
            params["in_loc"] = event.location

        return f"https://calendar.aol.com/?{urllib.parse.urlencode(params)}"

    def _generate_outlook_link(self, event: CalendarEvent) -> str:
        """Generate Microsoft Outlook link."""
        params = {
            "path": "/calendar/action/compose",
            "rru": "addevent",
            "subject": event.title,
            "startdt": event.start_time.isoformat(),
            "enddt": event.end_time.isoformat(),
        }

        if event.description:
            params["body"] = event.description

        if event.location:
            params["location"] = event.location

        return f"https://outlook.live.com/calendar/0/{urllib.parse.urlencode(params)}"

    def _generate_office365_link(self, event: CalendarEvent) -> str:
        """Generate Microsoft 365 link."""
        # Microsoft 365 uses the same format as Outlook
        return self._generate_outlook_link(event)

    def _format_google_dates(self, event: CalendarEvent) -> str:
        """Format dates for Google Calendar."""
        start_str = event.start_time.strftime("%Y%m%dT%H%M%SZ")
        end_str = event.end_time.strftime("%Y%m%dT%H%M%SZ")
        return f"{start_str}/{end_str}"

    def _format_yahoo_datetime(self, dt: datetime) -> str:
        """Format datetime for Yahoo/AOL Calendar."""
        return dt.strftime("%Y%m%dT%H%M%SZ")

    def get_supported_services(self) -> Dict[str, str]:
        """Get list of supported calendar services."""
        return self.SUPPORTED_SERVICES.copy() 