# Calendar Generator

Learn how to generate calendar links and ICS files for various calendar services.

## Overview

The `CalendarGenerator` class is responsible for creating calendar links and ICS files for different calendar services. It supports multiple popular calendar platforms and provides a unified interface for generating links.

## Supported Services

| Service | Method | URL Format | Features |
|---------|--------|------------|----------|
| Google Calendar | `"google"` | `https://calendar.google.com/...` | ✅ Attendees, Description, Location |
| Apple Calendar | `"apple"` | `webcal://calendar.apple.com/...` | ✅ Description, Location |
| Yahoo Calendar | `"yahoo"` | `https://calendar.yahoo.com/...` | ✅ Description, Location |
| AOL Calendar | `"aol"` | `https://calendar.aol.com/...` | ✅ Description, Location |
| Microsoft Outlook | `"outlook"` | `https://outlook.live.com/...` | ✅ Description, Location |
| Microsoft 365 | `"office365"` | `https://outlook.live.com/...` | ✅ Description, Location |
| ICS File | `"ics"` | Standard iCalendar format | ✅ Full iCalendar support |

## Basic Usage

### Initialize the Generator

```python
from calendar_link import CalendarGenerator

generator = CalendarGenerator()
```

### Generate Single Link

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

# Create an event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    description="Weekly team sync meeting",
    location="Conference Room A"
)

# Initialize generator
generator = CalendarGenerator()

# Generate Google Calendar link
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")

# Generate Apple Calendar link
apple_link = generator.generate_link(event, "apple")
print(f"Apple Calendar: {apple_link}")
```

### Generate All Links

```python
# Generate links for all supported services
all_links = generator.generate_all_links(event)

for service, link in all_links.items():
    print(f"{service.upper()}: {link}")
```

## Service-Specific Features

### Google Calendar

Google Calendar supports the most features:

```python
event = CalendarEvent(
    title="Client Meeting",
    start_time=datetime(2024, 1, 15, 14, 0),
    end_time=datetime(2024, 1, 15, 15, 0),
    description="Quarterly client presentation",
    location="Virtual Meeting Room",
    attendees=["client@example.com", "manager@example.com"]
)

google_link = generator.generate_link(event, "google")
```

**Features:**
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ✅ Attendees (comma-separated)

### Apple Calendar

Apple Calendar uses a custom URL scheme:

```python
apple_link = generator.generate_link(event, "apple")
# Returns: webcal://calendar.apple.com/event?title=...&start=...&end=...
```

**Features:**
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported by Apple Calendar URLs)

### Microsoft Services (Outlook & Office 365)

Both Outlook and Office 365 use the same format:

```python
outlook_link = generator.generate_link(event, "outlook")
office365_link = generator.generate_link(event, "office365")
```

**Features:**
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported in URL format)

### Yahoo & AOL Calendar

Both services use similar formats:

```python
yahoo_link = generator.generate_link(event, "yahoo")
aol_link = generator.generate_link(event, "aol")
```

**Features:**
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported)

## ICS File Generation

### Basic ICS Generation

```python
# Generate ICS file content
ics_content = generator.generate_ics(event)

# Save to file
with open("event.ics", "w") as f:
    f.write(ics_content)
```

### ICS with All Features

```python
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    description="Weekly team sync meeting",
    location="Conference Room A",
    attendees=["john@example.com", "jane@example.com"]
)

ics_content = generator.generate_ics(event)
```

**ICS Features:**
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ✅ Attendees
- ✅ Standard iCalendar format
- ✅ Compatible with all calendar applications

## Error Handling

### Unsupported Service

```python
from calendar_link.exceptions import UnsupportedCalendarServiceError

try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Error: {e}")
    # Error: Unsupported service: invalid_service. 
    # Supported services: ['google', 'apple', 'yahoo', 'aol', 'outlook', 'office365', 'ics']
```

### Case Insensitive Service Names

Service names are case-insensitive:

```python
# These all work the same
google_link1 = generator.generate_link(event, "google")
google_link2 = generator.generate_link(event, "GOOGLE")
google_link3 = generator.generate_link(event, "Google")

assert google_link1 == google_link2 == google_link3
```

## Advanced Usage

### Batch Link Generation

```python
def generate_links_for_events(events, services=None):
    """Generate links for multiple events."""
    if services is None:
        services = ["google", "apple", "outlook"]
    
    generator = CalendarGenerator()
    results = {}
    
    for i, event in enumerate(events):
        event_links = {}
        for service in services:
            try:
                link = generator.generate_link(event, service)
                event_links[service] = link
            except Exception as e:
                event_links[service] = f"Error: {str(e)}"
        
        results[f"event_{i+1}"] = event_links
    
    return results

# Example usage
events = [
    CalendarEvent(title="Meeting 1", start_time=datetime(2024, 1, 15, 10, 0)),
    CalendarEvent(title="Meeting 2", start_time=datetime(2024, 1, 15, 14, 0))
]

all_links = generate_links_for_events(events)
```

### Service Information

```python
# Get list of supported services
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

## Best Practices

1. **Always handle errors**: Wrap link generation in try-catch blocks
2. **Use appropriate services**: Different services have different feature support
3. **Validate events first**: Ensure events are valid before generating links
4. **Consider timezones**: Use timezone-aware datetimes for better compatibility
5. **Test with multiple services**: Verify links work across different platforms
6. **Use ICS for maximum compatibility**: ICS files work with all calendar applications

## Service Limitations

| Service | Attendees | Description | Location | Timezone Support |
|---------|-----------|-------------|----------|------------------|
| Google Calendar | ✅ | ✅ | ✅ | ✅ |
| Apple Calendar | ❌ | ✅ | ✅ | ✅ |
| Yahoo Calendar | ❌ | ✅ | ✅ | ✅ |
| AOL Calendar | ❌ | ✅ | ✅ | ✅ |
| Microsoft Outlook | ❌ | ✅ | ✅ | ✅ |
| Microsoft 365 | ❌ | ✅ | ✅ | ✅ |
| ICS File | ✅ | ✅ | ✅ | ✅ |

## Next Steps

- [Supported Services](supported-services.md) - Detailed service information
- [Timezone Handling](timezone-handling.md) - Advanced timezone features
- [Error Handling](error-handling.md) - Comprehensive error handling guide
- [API Reference](../api/calendar-generator.md) - Complete API documentation 