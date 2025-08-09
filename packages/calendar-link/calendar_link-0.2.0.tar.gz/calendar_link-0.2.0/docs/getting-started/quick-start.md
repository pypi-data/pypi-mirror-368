# Quick Start

Get up and running with Calendar Link Generator in minutes!

## Basic Usage

### 1. Import the Package

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator
```

### 2. Create a Calendar Event

```python
# Create a simple event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),  # 10:00 AM
    end_time=datetime(2024, 1, 15, 11, 0),    # 11:00 AM
    description="Weekly team sync meeting",
    location="Conference Room A",
    attendees=["john@example.com", "jane@example.com"]
)
```

### 3. Generate Calendar Links

```python
# Initialize the generator
generator = CalendarGenerator()

# Generate Google Calendar link
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")

# Generate ICS file content
ics_content = generator.generate_ics(event)
print(f"ICS Content:\n{ics_content}")
```

## Complete Example

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

def main():
    # Create an event
    event = CalendarEvent(
        title="Project Kickoff",
        start_time=datetime(2024, 1, 15, 14, 30),  # 2:30 PM
        end_time=datetime(2024, 1, 15, 16, 0),     # 4:00 PM
        description="Initial project planning and team introduction",
        location="Virtual Meeting Room",
        attendees=["team@company.com", "stakeholders@company.com"]
    )
    
    # Initialize generator
    generator = CalendarGenerator()
    
    # Generate links for different services
    services = ["google", "apple", "yahoo", "outlook"]
    
    for service in services:
        link = generator.generate_link(event, service)
        print(f"{service.upper()}: {link}")
    
    # Generate ICS file
    ics_content = generator.generate_ics(event)
    
    # Save ICS file
    with open("project_kickoff.ics", "w") as f:
        f.write(ics_content)
    print("ICS file saved as 'project_kickoff.ics'")

if __name__ == "__main__":
    main()
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

## Event Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `title` | str | ✅ | Event title/summary |
| `start_time` | datetime | ✅ | Event start time |
| `end_time` | datetime | ❌ | Event end time (defaults to start + 1 hour) |
| `description` | str | ❌ | Event description |
| `location` | str | ❌ | Event location |
| `attendees` | List[str] | ❌ | List of attendee email addresses |
| `all_day` | bool | ❌ | Whether this is an all-day event |
| `timezone` | str | ❌ | Timezone for the event |

## Quick Tips

### All-Day Events

```python
event = CalendarEvent(
    title="Company Holiday",
    start_time=datetime(2024, 1, 15, 0, 0),
    end_time=datetime(2024, 1, 15, 0, 0),
    all_day=True
)
```

### Events with Timezone

```python
import pytz

ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="Client Meeting",
    start_time=start_time,
    timezone="America/New_York"
)
```

### Generate All Links at Once

```python
all_links = generator.generate_all_links(event)
for service, link in all_links.items():
    print(f"{service}: {link}")
```

## Next Steps

- [Basic Usage](basic-usage.md) - Learn more about event creation and validation
- [Supported Services](../user-guide/supported-services.md) - Detailed information about each calendar service
- [Timezone Handling](../user-guide/timezone-handling.md) - Advanced timezone features
- [API Reference](../api/calendar-event.md) - Complete API documentation 