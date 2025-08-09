# Calendar Events

Learn how to create and manage calendar events with the Calendar Link Generator.

## Event Properties

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | str | Event title/summary (required) |
| `start_time` | datetime | Event start time (required) |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `end_time` | datetime | `start_time + 1 hour` | Event end time |
| `description` | str | None | Event description |
| `location` | str | None | Event location |
| `attendees` | List[str] | [] | List of attendee email addresses |
| `all_day` | bool | False | Whether this is an all-day event |
| `timezone` | str | Auto-detected | Timezone for the event |

## Creating Events

### Basic Event

```python
from datetime import datetime
from calendar_link import CalendarEvent

event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0)
)
```

### Event with All Properties

```python
import pytz

# Create timezone-aware datetime
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))
end_time = ny_tz.localize(datetime(2024, 1, 15, 11, 0))

event = CalendarEvent(
    title="Client Meeting",
    start_time=start_time,
    end_time=end_time,
    description="Quarterly client presentation and Q&A session",
    location="Conference Room A, 3rd Floor",
    attendees=["client@example.com", "manager@example.com", "sales@example.com"],
    all_day=False,
    timezone="America/New_York"
)
```

## Event Types

### Regular Events

Regular events have specific start and end times.

```python
event = CalendarEvent(
    title="Project Review",
    start_time=datetime(2024, 1, 15, 14, 0),
    end_time=datetime(2024, 1, 15, 16, 0),
    description="Monthly project status review"
)
```

### All-Day Events

All-day events span the entire day and should have 00:00 as the time.

```python
event = CalendarEvent(
    title="Company Holiday",
    start_time=datetime(2024, 1, 15, 0, 0),
    end_time=datetime(2024, 1, 15, 0, 0),
    all_day=True
)
```

### Multi-Day Events

Events that span multiple days.

```python
event = CalendarEvent(
    title="Conference",
    start_time=datetime(2024, 1, 15, 9, 0),
    end_time=datetime(2024, 1, 17, 17, 0),
    description="Annual developer conference"
)
```

## Timezone Handling

### Automatic Timezone Detection

If you provide a timezone-aware datetime, the timezone is automatically detected:

```python
import pytz

# Timezone-aware datetime
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="Meeting",
    start_time=start_time
)
# timezone will be "America/New_York"
```

### Explicit Timezone Specification

You can also specify the timezone explicitly:

```python
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"
)
```

### UTC Default

If no timezone is specified and the datetime is naive, UTC is used:

```python
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0)
)
# timezone will be "UTC"
```

## Event Validation

The `CalendarEvent` class performs several validations:

### Title Validation

```python
# This will raise InvalidEventDataError
event = CalendarEvent(
    title="",  # Empty title
    start_time=datetime(2024, 1, 15, 10, 0)
)
```

### Time Validation

```python
# This will raise InvalidEventDataError
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 11, 0),
    end_time=datetime(2024, 1, 15, 10, 0)  # End before start
)
```

### All-Day Event Validation

```python
# This will raise InvalidEventDataError
event = CalendarEvent(
    title="Holiday",
    start_time=datetime(2024, 1, 15, 10, 0),  # Not 00:00
    end_time=datetime(2024, 1, 15, 11, 0),    # Not 00:00
    all_day=True
)
```

## Event Methods

### Duration Calculation

```python
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 30)
)

duration_minutes = event.get_duration_minutes()
print(f"Event duration: {duration_minutes} minutes")  # 90 minutes
```

### Same Day Check

```python
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0)
)

if event.is_same_day():
    print("Event is on a single day")
else:
    print("Event spans multiple days")
```

### Dictionary Conversion

```python
# Convert to dictionary
event_dict = event.to_dict()
print(event_dict)
# {
#     "title": "Meeting",
#     "start_time": "2024-01-15T10:00:00",
#     "end_time": "2024-01-15T11:00:00",
#     "description": None,
#     "location": None,
#     "attendees": [],
#     "all_day": False,
#     "timezone": "UTC"
# }

# Create from dictionary
event = CalendarEvent.from_dict(event_dict)
```

## Best Practices

1. **Always provide a meaningful title**: This is what users will see in their calendar
2. **Use timezone-aware datetimes**: For better compatibility across services
3. **Validate attendee emails**: Use the utility functions to validate email addresses
4. **Handle all-day events correctly**: Set both start and end times to 00:00
5. **Provide clear descriptions**: Help attendees understand what to expect
6. **Include location when relevant**: Physical or virtual meeting locations

## Common Patterns

### Recurring Event Pattern

```python
from datetime import datetime, timedelta

def create_recurring_event(base_date, title, start_hour, duration_hours, weeks=4):
    events = []
    for week in range(weeks):
        event_date = base_date + timedelta(weeks=week)
        start_time = datetime.combine(event_date, datetime.min.time()) + timedelta(hours=start_hour)
        end_time = start_time + timedelta(hours=duration_hours)
        
        event = CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time
        )
        events.append(event)
    
    return events

# Create weekly team meetings
base_date = datetime(2024, 1, 15).date()
weekly_meetings = create_recurring_event(
    base_date=base_date,
    title="Weekly Team Sync",
    start_hour=10,
    duration_hours=1,
    weeks=8
)
```

### Batch Event Creation

```python
def create_events_from_data(event_data_list):
    events = []
    for data in event_data_list:
        try:
            event = CalendarEvent.from_dict(data)
            events.append(event)
        except InvalidEventDataError as e:
            print(f"Invalid event data: {e}")
            continue
    return events

# Example usage
event_data = [
    {
        "title": "Meeting 1",
        "start_time": "2024-01-15T10:00:00",
        "end_time": "2024-01-15T11:00:00"
    },
    {
        "title": "Meeting 2",
        "start_time": "2024-01-15T14:00:00",
        "end_time": "2024-01-15T15:00:00"
    }
]

events = create_events_from_data(event_data)
```

## Next Steps

- [Calendar Generator](calendar-generator.md) - Learn about generating calendar links
- [Supported Services](supported-services.md) - Service-specific information
- [Timezone Handling](timezone-handling.md) - Advanced timezone features
- [API Reference](../api/calendar-event.md) - Complete API documentation 