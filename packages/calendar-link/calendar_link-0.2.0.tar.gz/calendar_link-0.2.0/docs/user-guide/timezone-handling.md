# Timezone Handling

Learn how to work with timezones in the Calendar Link Generator.

## Overview

The Calendar Link Generator provides comprehensive timezone support to ensure events are displayed correctly across different calendar services and timezones.

## Basic Timezone Usage

### Timezone-Aware Datetimes

```python
import pytz
from datetime import datetime
from calendar_link import CalendarEvent

# Create timezone-aware datetime
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="Meeting",
    start_time=start_time
)
```

### Explicit Timezone Specification

```python
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"
)
```

## Common Timezones

### US Timezones

```python
# Eastern Time
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"
)

# Central Time
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/Chicago"
)

# Mountain Time
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/Denver"
)

# Pacific Time
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/Los_Angeles"
)
```

### International Timezones

```python
# UTC
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="UTC"
)

# London
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="Europe/London"
)

# Tokyo
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="Asia/Tokyo"
)

# Sydney
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="Australia/Sydney"
)
```

## Timezone Conversion

### Converting Between Timezones

```python
import pytz
from datetime import datetime

# Create event in one timezone
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

event = CalendarEvent(
    title="Meeting",
    start_time=start_time,
    timezone="America/New_York"
)

# Convert to different timezone for display
la_tz = pytz.timezone("America/Los_Angeles")
la_time = start_time.astimezone(la_tz)
print(f"Meeting time in LA: {la_time}")
```

### Working with UTC

```python
# Always store in UTC for consistency
utc_time = datetime(2024, 1, 15, 15, 0, tzinfo=pytz.UTC)

event = CalendarEvent(
    title="Meeting",
    start_time=utc_time,
    timezone="UTC"
)
```

## Daylight Saving Time

### Automatic DST Handling

The Calendar Link Generator automatically handles daylight saving time transitions:

```python
# This will automatically adjust for DST
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 3, 10, 10, 0),  # DST transition day
    timezone="America/New_York"
)
```

### Checking DST Status

```python
import pytz
from datetime import datetime

ny_tz = pytz.timezone("America/New_York")
dt = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

# Check if DST is in effect
is_dst = dt.dst() != timedelta(0)
print(f"Is DST: {is_dst}")
```

## Best Practices

### 1. Use Timezone-Aware Datetimes

```python
# Good: Timezone-aware
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(datetime(2024, 1, 15, 10, 0))

# Avoid: Naive datetime
start_time = datetime(2024, 1, 15, 10, 0)  # No timezone info
```

### 2. Store in UTC, Display in Local

```python
# Store events in UTC
utc_time = datetime(2024, 1, 15, 15, 0, tzinfo=pytz.UTC)

event = CalendarEvent(
    title="Meeting",
    start_time=utc_time,
    timezone="UTC"
)

# Convert for display
local_tz = pytz.timezone("America/New_York")
local_time = utc_time.astimezone(local_tz)
```

### 3. Handle Multiple Timezones

```python
def create_timezone_aware_event(title, local_time, timezone):
    """Create an event with proper timezone handling."""
    tz_obj = pytz.timezone(timezone)
    start_time = tz_obj.localize(local_time)
    
    return CalendarEvent(
        title=title,
        start_time=start_time,
        timezone=timezone
    )

# Create events in different timezones
ny_event = create_timezone_aware_event(
    "NY Meeting",
    datetime(2024, 1, 15, 10, 0),
    "America/New_York"
)

la_event = create_timezone_aware_event(
    "LA Meeting",
    datetime(2024, 1, 15, 10, 0),
    "America/Los_Angeles"
)
```

### 4. Validate Timezones

```python
from calendar_link.utils import get_timezone_offset

def validate_timezone(timezone):
    """Validate that a timezone is supported."""
    try:
        offset = get_timezone_offset(timezone)
        return True
    except:
        return False

# Check if timezone is valid
if validate_timezone("America/New_York"):
    event = CalendarEvent(
        title="Meeting",
        start_time=datetime(2024, 1, 15, 10, 0),
        timezone="America/New_York"
    )
```

## Common Issues

### Issue 1: Naive Datetime

```python
# Problem: No timezone information
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0)  # Naive datetime
)

# Solution: Add timezone
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"
)
```

### Issue 2: Ambiguous Times

```python
# Problem: Ambiguous time during DST transition
dt = datetime(2024, 11, 3, 2, 30)  # Ambiguous during fallback

# Solution: Use is_dst parameter
ny_tz = pytz.timezone("America/New_York")
start_time = ny_tz.localize(dt, is_dst=False)  # Specify DST preference
```

### Issue 3: Invalid Timezone

```python
# Problem: Invalid timezone name
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="Invalid/Timezone"  # Invalid
)

# Solution: Use valid timezone
event = CalendarEvent(
    title="Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"  # Valid
)
```

## Utility Functions

### Get Timezone Offset

```python
from calendar_link.utils import get_timezone_offset

# Get offset in minutes
offset = get_timezone_offset("America/New_York")
print(f"NY offset: {offset} minutes")
```

### Format Datetime for Service

```python
from calendar_link.utils import format_datetime_for_service

dt = datetime(2024, 1, 15, 10, 0)

# Format for Google Calendar
google_format = format_datetime_for_service(dt, "google")
print(f"Google format: {google_format}")

# Format for Outlook
outlook_format = format_datetime_for_service(dt, "outlook")
print(f"Outlook format: {outlook_format}")
```

## Next Steps

- [Calendar Events](calendar-events.md) - Learn about event creation
- [Calendar Generator](calendar-generator.md) - Generate calendar links
- [Error Handling](error-handling.md) - Handle timezone errors
- [API Reference](../api/utils.md) - Complete utility function documentation 