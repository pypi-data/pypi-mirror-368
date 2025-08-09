# Basic Usage

Learn the fundamental concepts and patterns for using the Calendar Link Generator.

## Core Concepts

The Calendar Link Generator consists of two main components:

1. **CalendarEvent**: Represents a calendar event with all its details
2. **CalendarGenerator**: Creates calendar links and ICS files for various services

## Creating Events

### Basic Event

```python
from datetime import datetime
from calendar_link import CalendarEvent

# Create a simple event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),  # 10:00 AM
    end_time=datetime(2024, 1, 15, 11, 0),    # 11:00 AM
    description="Weekly team sync meeting",
    location="Conference Room A"
)
```

### Event with Attendees

```python
event = CalendarEvent(
    title="Client Presentation",
    start_time=datetime(2024, 1, 15, 14, 0),
    end_time=datetime(2024, 1, 15, 15, 30),
    description="Quarterly client presentation",
    location="Virtual Meeting Room",
    attendees=["client@example.com", "manager@example.com"]
)
```

### All-Day Event

```python
event = CalendarEvent(
    title="Company Holiday",
    start_time=datetime(2024, 1, 15, 0, 0),
    end_time=datetime(2024, 1, 15, 0, 0),
    all_day=True
)
```

## Generating Calendar Links

### Single Service

```python
from calendar_link import CalendarGenerator

generator = CalendarGenerator()

# Generate Google Calendar link
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")

# Generate Apple Calendar link
apple_link = generator.generate_link(event, "apple")
print(f"Apple Calendar: {apple_link}")
```

### All Services at Once

```python
# Generate links for all supported services
all_links = generator.generate_all_links(event)

for service, link in all_links.items():
    print(f"{service.upper()}: {link}")
```

## Generating ICS Files

```python
# Generate ICS file content
ics_content = generator.generate_ics(event)

# Save to file
with open("event.ics", "w") as f:
    f.write(ics_content)
```

## Supported Services

| Service | Method | Description |
|---------|--------|-------------|
| Google Calendar | `"google"` | Google Calendar web interface |
| Apple Calendar | `"apple"` | Apple Calendar app |
| Yahoo Calendar | `"yahoo"` | Yahoo Calendar web interface |
| AOL Calendar | `"aol"` | AOL Calendar web interface |
| Microsoft Outlook | `"outlook"` | Outlook web interface |
| Microsoft 365 | `"office365"` | Microsoft 365 web interface |
| ICS File | `"ics"` | Standard iCalendar format |

## Error Handling

```python
from calendar_link.exceptions import InvalidEventDataError, UnsupportedCalendarServiceError

try:
    event = CalendarEvent(
        title="",  # Empty title will raise error
        start_time=datetime(2024, 1, 15, 10, 0)
    )
except InvalidEventDataError as e:
    print(f"Invalid event: {e}")

try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Unsupported service: {e}")
```

## Best Practices

1. **Always validate event data**: The `CalendarEvent` class performs validation automatically
2. **Use timezone-aware datetimes**: For better compatibility across services
3. **Sanitize text**: Use the utility functions for cleaning event descriptions
4. **Handle errors gracefully**: Wrap operations in try-catch blocks
5. **Test with multiple services**: Different services have different requirements

## Next Steps

- [Quick Start Guide](quick-start.md) - Get up and running quickly
- [Calendar Events](../user-guide/calendar-events.md) - Detailed event creation guide
- [Supported Services](../user-guide/supported-services.md) - Service-specific information
- [API Reference](../api/calendar-event.md) - Complete API documentation 