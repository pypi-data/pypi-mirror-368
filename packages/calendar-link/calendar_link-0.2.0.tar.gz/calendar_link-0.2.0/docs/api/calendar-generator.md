# CalendarGenerator

API reference for the CalendarGenerator class.

## Class Overview

The `CalendarGenerator` class is responsible for generating calendar links and ICS files for various calendar services.

## Constructor

```python
CalendarGenerator()
```

Creates a new calendar generator instance.

## Methods

### generate_link

```python
generate_link(event: CalendarEvent, service: str) -> str
```

Generate a calendar link for the specified service.

**Parameters:**
- `event` (CalendarEvent): The calendar event
- `service` (str): Calendar service name (google, apple, yahoo, aol, outlook, office365)

**Returns:**
- `str`: URL string for the calendar service

**Raises:**
- `UnsupportedCalendarServiceError`: If service is not supported

**Example:**
```python
generator = CalendarGenerator()
event = CalendarEvent(title="Meeting", start_time=datetime(2024, 1, 15, 10, 0))
link = generator.generate_link(event, "google")
```

### generate_ics

```python
generate_ics(event: CalendarEvent) -> str
```

Generate ICS file content for the event.

**Parameters:**
- `event` (CalendarEvent): The calendar event

**Returns:**
- `str`: ICS file content as string

**Example:**
```python
ics_content = generator.generate_ics(event)
with open("event.ics", "w") as f:
    f.write(ics_content)
```

### generate_all_links

```python
generate_all_links(event: CalendarEvent) -> Dict[str, str]
```

Generate links for all supported services.

**Parameters:**
- `event` (CalendarEvent): The calendar event

**Returns:**
- `Dict[str, str]`: Dictionary mapping service names to their URLs

**Example:**
```python
all_links = generator.generate_all_links(event)
for service, link in all_links.items():
    print(f"{service}: {link}")
```

### get_supported_services

```python
get_supported_services() -> Dict[str, str]
```

Get list of supported calendar services.

**Returns:**
- `Dict[str, str]`: Dictionary mapping service codes to display names

**Example:**
```python
services = generator.get_supported_services()
print(services)
# {
#     'google': 'Google Calendar',
#     'apple': 'Apple Calendar',
#     'yahoo': 'Yahoo Calendar',
#     'aol': 'AOL Calendar',
#     'outlook': 'Microsoft Outlook',
#     'office365': 'Microsoft 365',
#     'ics': 'ICS File'
# }
```

## Class Attributes

### SUPPORTED_SERVICES

```python
SUPPORTED_SERVICES: Dict[str, str]
```

Dictionary of supported calendar services and their display names.

## Private Methods

### _generate_google_link

```python
_generate_google_link(event: CalendarEvent) -> str
```

Generate Google Calendar link.

### _generate_apple_link

```python
_generate_apple_link(event: CalendarEvent) -> str
```

Generate Apple Calendar link.

### _generate_yahoo_link

```python
_generate_yahoo_link(event: CalendarEvent) -> str
```

Generate Yahoo Calendar link.

### _generate_aol_link

```python
_generate_aol_link(event: CalendarEvent) -> str
```

Generate AOL Calendar link.

### _generate_outlook_link

```python
_generate_outlook_link(event: CalendarEvent) -> str
```

Generate Microsoft Outlook link.

### _generate_office365_link

```python
_generate_office365_link(event: CalendarEvent) -> str
```

Generate Microsoft 365 link.

### _format_google_dates

```python
_format_google_dates(event: CalendarEvent) -> str
```

Format dates for Google Calendar.

### _format_yahoo_datetime

```python
_format_yahoo_datetime(dt: datetime) -> str
```

Format datetime for Yahoo/AOL Calendar.

## Usage Examples

### Basic Usage

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

# Create event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    description="Weekly team sync",
    location="Conference Room A"
)

# Initialize generator
generator = CalendarGenerator()

# Generate single link
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")

# Generate all links
all_links = generator.generate_all_links(event)
for service, link in all_links.items():
    print(f"{service}: {link}")

# Generate ICS file
ics_content = generator.generate_ics(event)
with open("meeting.ics", "w") as f:
    f.write(ics_content)
```

### Error Handling

```python
from calendar_link.exceptions import UnsupportedCalendarServiceError

try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Error: {e}")
    # Get supported services
    services = generator.get_supported_services()
    print(f"Supported services: {list(services.keys())}")
```

### Service-Specific Features

```python
# Google Calendar (supports attendees)
event_with_attendees = CalendarEvent(
    title="Client Meeting",
    start_time=datetime(2024, 1, 15, 14, 0),
    attendees=["client@example.com", "manager@example.com"]
)
google_link = generator.generate_link(event_with_attendees, "google")

# Apple Calendar (no attendees in URL)
apple_link = generator.generate_link(event_with_attendees, "apple")

# ICS file (full support)
ics_content = generator.generate_ics(event_with_attendees)
```

## Service Support Matrix

| Feature | Google | Apple | Yahoo | AOL | Outlook | Office 365 | ICS |
|---------|--------|-------|-------|-----|---------|------------|-----|
| Event Title | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Start/End Time | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Description | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Location | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Attendees | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Timezone Support | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| All-Day Events | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Related

- [CalendarEvent](calendar-event.md) - Event data model
- [Exceptions](exceptions.md) - Error handling
- [Utilities](utils.md) - Helper functions 