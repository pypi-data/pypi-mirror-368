# Basic Examples

Simple examples to get you started with the Calendar Link Generator.

## Quick Start

### Create a Simple Event

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

# Create a basic event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0)
)

# Generate Google Calendar link
generator = CalendarGenerator()
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")
```

### Generate All Links

```python
# Generate links for all supported services
all_links = generator.generate_all_links(event)

for service, link in all_links.items():
    print(f"{service.upper()}: {link}")
```

## Event Types

### Regular Event

```python
event = CalendarEvent(
    title="Client Meeting",
    start_time=datetime(2024, 1, 15, 14, 0),
    end_time=datetime(2024, 1, 15, 15, 30),
    description="Quarterly client presentation",
    location="Conference Room A"
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

### Event with Attendees

```python
event = CalendarEvent(
    title="Team Sync",
    start_time=datetime(2024, 1, 15, 9, 0),
    end_time=datetime(2024, 1, 15, 9, 30),
    attendees=["john@example.com", "jane@example.com", "manager@example.com"]
)
```

## Service-Specific Examples

### Google Calendar

```python
# Google Calendar supports all features
event = CalendarEvent(
    title="Project Review",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    description="Monthly project status review",
    location="Virtual Meeting Room",
    attendees=["team@example.com", "stakeholder@example.com"]
)

google_link = generator.generate_link(event, "google")
```

### Apple Calendar

```python
# Apple Calendar (no attendees in URL)
event = CalendarEvent(
    title="Design Review",
    start_time=datetime(2024, 1, 15, 14, 0),
    end_time=datetime(2024, 1, 15, 15, 0),
    description="UI/UX design review session",
    location="Design Studio"
)

apple_link = generator.generate_link(event, "apple")
```

### ICS File

```python
# Generate ICS file for maximum compatibility
ics_content = generator.generate_ics(event)

# Save to file
with open("meeting.ics", "w") as f:
    f.write(ics_content)
```

## Timezone Examples

### Timezone-Aware Event

```python
import pytz

# Create timezone-aware datetime
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="NY Meeting",
    start_time=start_time,
    timezone="America/New_York"
)
```

### Multiple Timezones

```python
# Create events in different timezones
ny_event = CalendarEvent(
    title="NY Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"
)

la_event = CalendarEvent(
    title="LA Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/Los_Angeles"
)
```

## Error Handling Examples

### Invalid Event Data

```python
from calendar_link.exceptions import InvalidEventDataError

try:
    event = CalendarEvent(
        title="",  # Empty title
        start_time=datetime(2024, 1, 15, 10, 0)
    )
except InvalidEventDataError as e:
    print(f"Invalid event: {e}")
```

### Unsupported Service

```python
from calendar_link.exceptions import UnsupportedCalendarServiceError

try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Unsupported service: {e}")
```

## Utility Examples

### Email Validation

```python
from calendar_link.utils import validate_email

emails = ["user@example.com", "invalid-email", "test@domain.co.uk"]

for email in emails:
    if validate_email(email):
        print(f"✓ {email} is valid")
    else:
        print(f"✗ {email} is invalid")
```

### Text Sanitization

```python
from calendar_link.utils import sanitize_text

text = "  Meeting with <script>alert('xss')</script>  "
clean_text = sanitize_text(text)
print(clean_text)  # "Meeting with alert('xss')"
```

### Duration Calculation

```python
from calendar_link.utils import format_duration

event = CalendarEvent(
    title="Long Meeting",
    start_time=datetime(2024, 1, 15, 9, 0),
    end_time=datetime(2024, 1, 15, 11, 30)
)

duration = format_duration(event.get_duration_minutes())
print(f"Meeting duration: {duration}")  # "2 hours 30 minutes"
```

## Complete Example

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator
from calendar_link.utils import validate_email, sanitize_text

def create_meeting_event(title, start_time, end_time, attendees=None, location=None):
    """Create a meeting event with validation."""
    # Sanitize inputs
    clean_title = sanitize_text(title)
    clean_location = sanitize_text(location) if location else None
    
    # Validate attendees
    valid_attendees = []
    if attendees:
        for attendee in attendees:
            if validate_email(attendee):
                valid_attendees.append(attendee)
            else:
                print(f"Warning: Invalid email '{attendee}' will be ignored")
    
    # Create event
    event = CalendarEvent(
        title=clean_title,
        start_time=start_time,
        end_time=end_time,
        location=clean_location,
        attendees=valid_attendees
    )
    
    return event

def generate_all_links_for_meeting(title, start_time, end_time, attendees=None, location=None):
    """Generate all calendar links for a meeting."""
    # Create event
    event = create_meeting_event(title, start_time, end_time, attendees, location)
    
    # Generate all links
    generator = CalendarGenerator()
    all_links = generator.generate_all_links(event)
    
    # Print results
    print(f"Calendar links for: {event.title}")
    print(f"Time: {event.start_time} - {event.end_time}")
    print(f"Location: {event.location or 'No location'}")
    print(f"Attendees: {', '.join(event.attendees) if event.attendees else 'None'}")
    print("\nLinks:")
    
    for service, link in all_links.items():
        print(f"  {service.upper()}: {link}")
    
    return all_links

# Usage
meeting_links = generate_all_links_for_meeting(
    title="Weekly Team Sync",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    attendees=["john@example.com", "jane@example.com", "invalid-email"],
    location="Conference Room A"
)
```

## Next Steps

- [Advanced Examples](advanced-examples.md) - More complex usage patterns
- [Integration Examples](integration-examples.md) - Real-world integrations
- [User Guide](../user-guide/calendar-events.md) - Detailed event creation guide
- [API Reference](../api/calendar-event.md) - Complete API documentation 