# Calendar Link Generator

[![Tests](https://github.com/Nneji123/calendar-link/actions/workflows/tests.yml/badge.svg)](https://github.com/Nneji123/calendar-link/actions/workflows/tests.yml)
[![Deploy Docs](https://github.com/Nneji123/calendar-link/actions/workflows/docs.yml/badge.svg)](https://github.com/Nneji123/calendar-link/actions/workflows/docs.yml)
[![Codecov](https://github.com/Nneji123/calendar-link/actions/workflows/codecov.yml/badge.svg)](https://github.com/Nneji123/calendar-link/actions/workflows/codecov.yml)
[![Pypi](https://github.com/Nneji123/calendar-link/actions/workflows/pypi.yml/badge.svg)](https://github.com/Nneji123/calendar-link/actions/workflows/pypi.yml)

A Python package for generating calendar links and ICS files for various calendar services including Google Calendar, Apple Calendar, Yahoo Calendar, AOL Calendar, and Microsoft 365.

## Features

- Generate calendar links for multiple services:
  - Google Calendar
  - Apple Calendar
  - Yahoo Calendar
  - AOL Calendar
  - Microsoft Outlook
  - Microsoft 365
- Generate ICS (iCalendar) files
- Support for timezone handling
- Event validation and sanitization
- Comprehensive error handling

## Installation

```bash
pip install calendar-link
```

## Quick Start

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

# Create an event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),  # 10:00 AM
    end_time=datetime(2024, 1, 15, 11, 0),    # 11:00 AM
    description="Weekly team sync meeting",
    location="Conference Room A",
    attendees=["john@example.com", "jane@example.com"]
)

# Generate calendar links
generator = CalendarGenerator()

# Generate Google Calendar link
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")

# Generate ICS file content
ics_content = generator.generate_ics(event)
print(f"ICS Content:\n{ics_content}")

# Generate all links at once
all_links = generator.generate_all_links(event)
for service, link in all_links.items():
    print(f"{service}: {link}")
```

## Usage Examples

### Creating Events from Dictionary

```python
from calendar_link import CalendarEvent

event_data = {
    "title": "Birthday Party",
    "start_time": "2024-02-15T18:00:00",
    "end_time": "2024-02-15T22:00:00",
    "description": "Come celebrate!",
    "location": "My House",
    "all_day": False
}

event = CalendarEvent.from_dict(event_data)
```

### Working with Timezones

```python
import pytz
from datetime import datetime
from calendar_link import CalendarEvent

# Create event with specific timezone
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="Meeting",
    start_time=start_time,
    end_time=start_time.replace(hour=11),
    timezone="America/New_York"
)
```

### All-Day Events

```python
from datetime import datetime
from calendar_link import CalendarEvent

event = CalendarEvent(
    title="Vacation Day",
    start_time=datetime(2024, 1, 15, 0, 0),
    end_time=datetime(2024, 1, 15, 0, 0),
    all_day=True
)
```

### Saving ICS File

```python
from calendar_link import CalendarEvent, CalendarGenerator

event = CalendarEvent(
    title="Important Meeting",
    start_time=datetime(2024, 1, 15, 14, 30),
    end_time=datetime(2024, 1, 15, 15, 30),
    description="Don't forget to prepare the presentation"
)

generator = CalendarGenerator()
ics_content = generator.generate_ics(event)

# Save to file
with open("meeting.ics", "w") as f:
    f.write(ics_content)
```

## API Reference

### CalendarEvent

The main class for representing calendar events.

#### Constructor

```python
CalendarEvent(
    title: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    all_day: bool = False,
    timezone: Optional[str] = None
)
```

#### Methods

- `from_dict(data: dict) -> CalendarEvent`: Create event from dictionary
- `to_dict() -> dict`: Convert event to dictionary
- `get_duration_minutes() -> int`: Get event duration in minutes
- `is_same_day() -> bool`: Check if start and end are on same day

### CalendarGenerator

The main class for generating calendar links and ICS files.

#### Methods

- `generate_link(event: CalendarEvent, service: str) -> str`: Generate link for specific service
- `generate_ics(event: CalendarEvent) -> str`: Generate ICS file content
- `generate_all_links(event: CalendarEvent) -> Dict[str, str]`: Generate all links
- `get_supported_services() -> Dict[str, str]`: Get list of supported services

#### Supported Services

- `google`: Google Calendar
- `apple`: Apple Calendar
- `yahoo`: Yahoo Calendar
- `aol`: AOL Calendar
- `outlook`: Microsoft Outlook
- `office365`: Microsoft 365
- `ics`: ICS File

## Error Handling

The package includes custom exceptions for better error handling:

```python
from calendar_link import CalendarLinkError, InvalidEventDataError, UnsupportedCalendarServiceError

try:
    event = CalendarEvent(title="", start_time=datetime.now())  # Invalid title
except InvalidEventDataError as e:
    print(f"Invalid event data: {e}")

try:
    generator.generate_link(event, "unsupported_service")
except UnsupportedCalendarServiceError as e:
    print(f"Unsupported service: {e}")
```

## Utility Functions

The package also includes utility functions for common operations:

```python
from calendar_link.utils import parse_datetime, validate_email, sanitize_text

# Parse datetime with timezone
dt = parse_datetime("2024-01-15 10:00:00", "America/New_York")

# Validate email
is_valid = validate_email("user@example.com")

# Sanitize text for calendar services
clean_text = sanitize_text("Event\nDescription\nwith\nnewlines")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [ical](https://github.com/allenporter/ical) - Python iCalendar implementation
- [python-dateutil](https://dateutil.readthedocs.io/) - Date utilities
- [pytz](https://pythonhosted.org/pytz/) - Timezone handling