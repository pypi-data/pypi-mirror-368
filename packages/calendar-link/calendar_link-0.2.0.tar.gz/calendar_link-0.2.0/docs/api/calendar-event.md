# CalendarEvent

The main class for representing calendar events with validation and utility methods.

## Constructor

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

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `title` | str | ✅ | - | Event title/summary |
| `start_time` | datetime | ✅ | - | Event start time |
| `end_time` | datetime | ❌ | `start_time + 1 hour` | Event end time |
| `description` | str | ❌ | None | Event description |
| `location` | str | ❌ | None | Event location |
| `attendees` | List[str] | ❌ | [] | List of attendee email addresses |
| `all_day` | bool | ❌ | False | Whether this is an all-day event |
| `timezone` | str | ❌ | Auto-detected | Timezone for the event |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | str | Event title/summary |
| `start_time` | datetime | Event start time |
| `end_time` | datetime | Event end time |
| `description` | Optional[str] | Event description |
| `location` | Optional[str] | Event location |
| `attendees` | List[str] | List of attendee email addresses |
| `all_day` | bool | Whether this is an all-day event |
| `timezone` | str | Timezone for the event |

## Methods

### `from_dict(data: dict) -> CalendarEvent`

Create a CalendarEvent from a dictionary.

#### Parameters

- `data` (dict): Dictionary containing event data

#### Returns

- `CalendarEvent`: New CalendarEvent instance

#### Example

```python
event_data = {
    "title": "Meeting",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T11:00:00",
    "description": "Team meeting",
    "location": "Conference Room A"
}

event = CalendarEvent.from_dict(event_data)
```

### `to_dict() -> dict`

Convert event to dictionary.

#### Returns

- `dict`: Dictionary representation of the event

#### Example

```python
event_dict = event.to_dict()
# {
#     "title": "Meeting",
#     "start_time": "2024-01-15T10:00:00",
#     "end_time": "2024-01-15T11:00:00",
#     "description": "Team meeting",
#     "location": "Conference Room A",
#     "attendees": [],
#     "all_day": False,
#     "timezone": "UTC"
# }
```

### `get_duration_minutes() -> int`

Get event duration in minutes.

#### Returns

- `int`: Duration in minutes

#### Example

```python
duration = event.get_duration_minutes()
print(f"Event duration: {duration} minutes")
```

### `is_same_day() -> bool`

Check if start and end time are on the same day.

#### Returns

- `bool`: True if start and end are on the same day

#### Example

```python
if event.is_same_day():
    print("Event is on a single day")
else:
    print("Event spans multiple days")
```

## Validation

The CalendarEvent class performs several validations:

### Required Fields

- `title` must be provided and non-empty
- `start_time` must be provided

### Time Validation

- `end_time` must be after `start_time`
- For all-day events, both start and end times must be at 00:00

### Error Types

| Error | Condition | Message |
|-------|-----------|---------|
| `InvalidEventDataError` | Empty title | "Event title is required" |
| `InvalidEventDataError` | End before start | "Start time must be before end time" |
| `InvalidEventDataError` | All-day with time | "All-day events should have 00:00 as time" |

## Examples

### Basic Event

```python
from datetime import datetime
from calendar_link import CalendarEvent

event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    description="Weekly team sync",
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
    title="Client Meeting",
    start_time=datetime(2024, 1, 15, 14, 0),
    attendees=["client@example.com", "manager@example.com"]
)
```

### Event with Timezone

```python
import pytz

ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="Remote Meeting",
    start_time=start_time,
    timezone="America/New_York"
)
```

## Error Handling

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

## Related

- [CalendarGenerator](calendar-generator.md) - Generate calendar links
- [Exceptions](exceptions.md) - Error handling
- [Utilities](utils.md) - Helper functions 