# Utilities

API reference for utility functions in the Calendar Link Generator.

## Overview

The `utils` module provides helper functions for datetime parsing, email validation, text sanitization, and timezone operations.

## Datetime Functions

### parse_datetime

```python
parse_datetime(datetime_str: str, timezone: str = "UTC") -> datetime
```

Parse a datetime string into a timezone-aware datetime object.

**Parameters:**
- `datetime_str` (str): Datetime string to parse
- `timezone` (str): Timezone to apply (default: "UTC")

**Returns:**
- `datetime`: Timezone-aware datetime object

**Raises:**
- `ValueError`: If datetime string cannot be parsed

**Example:**
```python
from calendar_link.utils import parse_datetime

# Parse ISO format
dt = parse_datetime("2024-01-15T10:00:00")
print(dt)  # 2024-01-15 10:00:00+00:00

# Parse with timezone
dt = parse_datetime("2024-01-15T10:00:00", "America/New_York")
print(dt)  # 2024-01-15 10:00:00-05:00

# Parse various formats
dt1 = parse_datetime("2024-01-15 10:00:00")
dt2 = parse_datetime("Jan 15, 2024 10:00 AM")
dt3 = parse_datetime("15/01/2024 10:00")
```

### format_datetime_for_service

```python
format_datetime_for_service(dt: datetime, service: str) -> str
```

Format datetime for a specific calendar service.

**Parameters:**
- `dt` (datetime): Datetime to format
- `service` (str): Calendar service name

**Returns:**
- `str`: Formatted datetime string

**Example:**
```python
from calendar_link.utils import format_datetime_for_service

dt = datetime(2024, 1, 15, 10, 0)

# Google Calendar format
google_format = format_datetime_for_service(dt, "google")
print(google_format)  # "20240115T100000Z"

# Outlook format
outlook_format = format_datetime_for_service(dt, "outlook")
print(outlook_format)  # "2024-01-15T10:00:00"

# Apple format
apple_format = format_datetime_for_service(dt, "apple")
print(apple_format)  # "2024-01-15T10:00:00"
```

## Email Functions

### validate_email

```python
validate_email(email: str) -> bool
```

Validate email address format.

**Parameters:**
- `email` (str): Email address to validate

**Returns:**
- `bool`: True if valid email format, False otherwise

**Example:**
```python
from calendar_link.utils import validate_email

# Valid emails
print(validate_email("user@example.com"))  # True
print(validate_email("user.name@domain.co.uk"))  # True
print(validate_email("user+tag@example.com"))  # True

# Invalid emails
print(validate_email("invalid-email"))  # False
print(validate_email("@example.com"))  # False
print(validate_email("user@"))  # False
print(validate_email("user..name@example.com"))  # False
```

## Text Functions

### sanitize_text

```python
sanitize_text(text: str, max_length: int = 1000) -> str
```

Sanitize text for use in calendar events.

**Parameters:**
- `text` (str): Text to sanitize
- `max_length` (int): Maximum length (default: 1000)

**Returns:**
- `str`: Sanitized text

**Example:**
```python
from calendar_link.utils import sanitize_text

# Basic sanitization
text = "  Hello, World!  "
sanitized = sanitize_text(text)
print(sanitized)  # "Hello, World!"

# Truncate long text
long_text = "A" * 2000
truncated = sanitize_text(long_text, max_length=100)
print(len(truncated))  # 100

# Handle special characters
special_text = "Meeting with <script>alert('xss')</script>"
clean_text = sanitize_text(special_text)
print(clean_text)  # "Meeting with alert('xss')"
```

## Timezone Functions

### get_timezone_offset

```python
get_timezone_offset(timezone: str) -> int
```

Get timezone offset in minutes.

**Parameters:**
- `timezone` (str): Timezone name

**Returns:**
- `int`: Offset in minutes from UTC

**Raises:**
- `TimezoneError`: If timezone is invalid

**Example:**
```python
from calendar_link.utils import get_timezone_offset

# Get offsets
ny_offset = get_timezone_offset("America/New_York")
print(ny_offset)  # -300 (EST) or -240 (EDT)

la_offset = get_timezone_offset("America/Los_Angeles")
print(la_offset)  # -480 (PST) or -420 (PDT)

utc_offset = get_timezone_offset("UTC")
print(utc_offset)  # 0
```

### is_business_hours

```python
is_business_hours(dt: datetime, timezone: str = "UTC") -> bool
```

Check if datetime is during business hours (9 AM - 5 PM, Monday-Friday).

**Parameters:**
- `dt` (datetime): Datetime to check
- `timezone` (str): Timezone to check against (default: "UTC")

**Returns:**
- `bool`: True if during business hours, False otherwise

**Example:**
```python
from calendar_link.utils import is_business_hours

# Business hours
business_time = datetime(2024, 1, 15, 14, 0)  # Monday 2 PM
print(is_business_hours(business_time, "America/New_York"))  # True

# Outside business hours
evening_time = datetime(2024, 1, 15, 20, 0)  # Monday 8 PM
print(is_business_hours(evening_time, "America/New_York"))  # False

# Weekend
weekend_time = datetime(2024, 1, 13, 14, 0)  # Saturday 2 PM
print(is_business_hours(weekend_time, "America/New_York"))  # False
```

### get_next_business_day

```python
get_next_business_day(dt: datetime, timezone: str = "UTC") -> datetime
```

Get the next business day from the given datetime.

**Parameters:**
- `dt` (datetime): Starting datetime
- `timezone` (str): Timezone to use (default: "UTC")

**Returns:**
- `datetime`: Next business day at 9 AM

**Example:**
```python
from calendar_link.utils import get_next_business_day

# Friday to Monday
friday = datetime(2024, 1, 12, 15, 0)  # Friday 3 PM
monday = get_next_business_day(friday, "America/New_York")
print(monday)  # 2024-01-15 09:00:00-05:00 (Monday 9 AM)

# Weekend to Monday
saturday = datetime(2024, 1, 13, 10, 0)  # Saturday 10 AM
next_monday = get_next_business_day(saturday, "America/New_York")
print(next_monday)  # 2024-01-15 09:00:00-05:00 (Monday 9 AM)
```

## Duration Functions

### format_duration

```python
format_duration(minutes: int) -> str
```

Format duration in minutes to a human-readable string.

**Parameters:**
- `minutes` (int): Duration in minutes

**Returns:**
- `str`: Formatted duration string

**Example:**
```python
from calendar_link.utils import format_duration

# Various durations
print(format_duration(30))   # "30 minutes"
print(format_duration(60))   # "1 hour"
print(format_duration(90))   # "1 hour 30 minutes"
print(format_duration(120))  # "2 hours"
print(format_duration(1440)) # "1 day"
print(format_duration(0))    # "0 minutes"
```

## Usage Examples

### Event Creation with Utilities

```python
from datetime import datetime
from calendar_link.utils import parse_datetime, validate_email, sanitize_text
from calendar_link import CalendarEvent

def create_event_from_data(event_data):
    """Create event using utility functions."""
    # Parse datetime
    start_time = parse_datetime(event_data["start_time"])
    end_time = parse_datetime(event_data["end_time"])
    
    # Validate attendees
    valid_attendees = []
    for attendee in event_data.get("attendees", []):
        if validate_email(attendee):
            valid_attendees.append(attendee)
        else:
            print(f"Invalid email: {attendee}")
    
    # Sanitize text
    title = sanitize_text(event_data["title"])
    description = sanitize_text(event_data.get("description", ""))
    location = sanitize_text(event_data.get("location", ""))
    
    return CalendarEvent(
        title=title,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location,
        attendees=valid_attendees
    )

# Usage
event_data = {
    "title": "  Team Meeting  ",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "description": "Weekly team sync meeting",
    "location": "Conference Room A",
    "attendees": ["john@example.com", "invalid-email", "jane@example.com"]
}

event = create_event_from_data(event_data)
```

### Timezone-Aware Event Creation

```python
from calendar_link.utils import get_timezone_offset, is_business_hours

def create_business_event(title, start_time, timezone="America/New_York"):
    """Create event with business hours validation."""
    # Check if it's business hours
    if not is_business_hours(start_time, timezone):
        print(f"Warning: Event at {start_time} is outside business hours")
    
    # Get timezone offset for display
    offset = get_timezone_offset(timezone)
    offset_hours = offset // 60
    offset_sign = "+" if offset >= 0 else ""
    
    print(f"Event timezone: {timezone} (UTC{offset_sign}{offset_hours})")
    
    return CalendarEvent(
        title=title,
        start_time=start_time,
        timezone=timezone
    )

# Usage
event = create_business_event(
    "Client Meeting",
    datetime(2024, 1, 15, 14, 0),  # 2 PM
    "America/New_York"
)
```

### Batch Email Validation

```python
from calendar_link.utils import validate_email

def validate_attendee_list(attendees):
    """Validate a list of email addresses."""
    valid_emails = []
    invalid_emails = []
    
    for email in attendees:
        if validate_email(email):
            valid_emails.append(email)
        else:
            invalid_emails.append(email)
    
    if invalid_emails:
        print("Invalid email addresses:")
        for email in invalid_emails:
            print(f"  - {email}")
    
    return valid_emails

# Usage
attendees = [
    "john@example.com",
    "invalid-email",
    "jane@example.com",
    "@domain.com",
    "user@example.com"
]

valid_attendees = validate_attendee_list(attendees)
print(f"Valid attendees: {valid_attendees}")
```

### Duration Calculation

```python
from calendar_link.utils import format_duration

def calculate_event_duration(event):
    """Calculate and format event duration."""
    duration_minutes = event.get_duration_minutes()
    return format_duration(duration_minutes)

# Usage
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 30)
)

duration = calculate_event_duration(event)
print(f"Event duration: {duration}")  # "1 hour 30 minutes"
```

## Error Handling

### Timezone Validation

```python
from calendar_link.utils import get_timezone_offset
from calendar_link.exceptions import TimezoneError

def validate_timezone(timezone):
    """Validate timezone and return offset."""
    try:
        offset = get_timezone_offset(timezone)
        return offset
    except TimezoneError as e:
        print(f"Invalid timezone '{timezone}': {e}")
        return None

# Usage
timezones = ["America/New_York", "Invalid/Timezone", "UTC"]

for tz in timezones:
    offset = validate_timezone(tz)
    if offset is not None:
        print(f"{tz}: UTC{offset:+d} minutes")
    else:
        print(f"{tz}: Invalid timezone")
```

### Datetime Parsing with Error Handling

```python
from calendar_link.utils import parse_datetime

def safe_parse_datetime(datetime_str, timezone="UTC"):
    """Safely parse datetime string."""
    try:
        return parse_datetime(datetime_str, timezone)
    except ValueError as e:
        print(f"Failed to parse datetime '{datetime_str}': {e}")
        return None

# Usage
datetime_strings = [
    "2024-01-15T10:00:00",
    "invalid-datetime",
    "Jan 15, 2024 10:00 AM"
]

for dt_str in datetime_strings:
    dt = safe_parse_datetime(dt_str)
    if dt:
        print(f"Parsed: {dt}")
    else:
        print(f"Failed to parse: {dt_str}")
```

## Best Practices

### 1. Always Validate Input

```python
def create_event_safely(title, start_time_str, attendees=None):
    """Create event with input validation."""
    # Validate title
    if not title or not title.strip():
        raise ValueError("Title is required")
    
    # Parse datetime
    try:
        start_time = parse_datetime(start_time_str)
    except ValueError as e:
        raise ValueError(f"Invalid start time: {e}")
    
    # Validate attendees
    valid_attendees = []
    if attendees:
        for attendee in attendees:
            if validate_email(attendee):
                valid_attendees.append(attendee)
            else:
                print(f"Warning: Invalid email '{attendee}' will be ignored")
    
    return CalendarEvent(
        title=sanitize_text(title),
        start_time=start_time,
        attendees=valid_attendees
    )
```

### 2. Use Type Hints

```python
from typing import List, Optional
from datetime import datetime

def validate_emails(emails: List[str]) -> List[str]:
    """Validate list of email addresses."""
    return [email for email in emails if validate_email(email)]

def format_event_time(dt: datetime, service: str) -> str:
    """Format datetime for specific service."""
    return format_datetime_for_service(dt, service)
```

### 3. Handle Edge Cases

```python
def safe_sanitize_text(text: Optional[str], max_length: int = 1000) -> str:
    """Safely sanitize text with edge case handling."""
    if text is None:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    return sanitize_text(text, max_length)

def get_timezone_info(timezone: str) -> Optional[dict]:
    """Get timezone information with error handling."""
    try:
        offset = get_timezone_offset(timezone)
        return {
            "timezone": timezone,
            "offset_minutes": offset,
            "offset_hours": offset // 60,
            "is_utc": offset == 0
        }
    except TimezoneError:
        return None
```

## Related

- [CalendarEvent](calendar-event.md) - Event data model
- [CalendarGenerator](calendar-generator.md) - Link generation
- [Exceptions](exceptions.md) - Error handling 