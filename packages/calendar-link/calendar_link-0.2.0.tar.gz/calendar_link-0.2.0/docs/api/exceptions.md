# Exceptions

API reference for custom exceptions in the Calendar Link Generator.

## Exception Hierarchy

```
CalendarLinkError (base)
├── InvalidEventDataError
├── UnsupportedCalendarServiceError
└── TimezoneError
```

## CalendarLinkError

Base exception for all calendar link errors.

```python
class CalendarLinkError(Exception):
    """Base exception for calendar link errors."""
```

**Inherits from:** `Exception`

**Usage:**
```python
from calendar_link.exceptions import CalendarLinkError

try:
    # Some operation
    pass
except CalendarLinkError as e:
    print(f"Calendar error: {e}")
```

## InvalidEventDataError

Raised when event data is invalid.

```python
class InvalidEventDataError(CalendarLinkError):
    """Raised when event data is invalid."""
```

**Inherits from:** `CalendarLinkError`

**Common Causes:**
- Empty or whitespace-only title
- End time before start time
- Invalid all-day event times

**Usage:**
```python
from calendar_link.exceptions import InvalidEventDataError

try:
    event = CalendarEvent(
        title="",  # Empty title
        start_time=datetime(2024, 1, 15, 10, 0)
    )
except InvalidEventDataError as e:
    print(f"Invalid event: {e}")
    # Output: Invalid event: Event title is required
```

**Examples:**
```python
# Empty title
try:
    event = CalendarEvent(title="", start_time=datetime(2024, 1, 15, 10, 0))
except InvalidEventDataError as e:
    print(e)  # "Event title is required"

# End before start
try:
    event = CalendarEvent(
        title="Meeting",
        start_time=datetime(2024, 1, 15, 11, 0),
        end_time=datetime(2024, 1, 15, 10, 0)
    )
except InvalidEventDataError as e:
    print(e)  # "Start time must be before end time"

# Invalid all-day event
try:
    event = CalendarEvent(
        title="Holiday",
        start_time=datetime(2024, 1, 15, 10, 0),  # Not 00:00
        end_time=datetime(2024, 1, 15, 11, 0),    # Not 00:00
        all_day=True
    )
except InvalidEventDataError as e:
    print(e)  # "All-day events should have 00:00 as time"
```

## UnsupportedCalendarServiceError

Raised when an unsupported calendar service is requested.

```python
class UnsupportedCalendarServiceError(CalendarLinkError):
    """Raised when an unsupported calendar service is requested."""
```

**Inherits from:** `CalendarLinkError`

**Usage:**
```python
from calendar_link.exceptions import UnsupportedCalendarServiceError

try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Unsupported service: {e}")
    # Output: Unsupported service: invalid_service. 
    # Supported services: ['google', 'apple', 'yahoo', 'aol', 'outlook', 'office365', 'ics']
```

**Supported Services:**
- `"google"` - Google Calendar
- `"apple"` - Apple Calendar
- `"yahoo"` - Yahoo Calendar
- `"aol"` - AOL Calendar
- `"outlook"` - Microsoft Outlook
- `"office365"` - Microsoft 365
- `"ics"` - ICS File

**Example:**
```python
generator = CalendarGenerator()

# Valid service
try:
    link = generator.generate_link(event, "google")
    print("Link generated successfully")
except UnsupportedCalendarServiceError as e:
    print(f"Error: {e}")

# Invalid service
try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Error: {e}")
    # Get supported services
    services = generator.get_supported_services()
    print(f"Supported services: {list(services.keys())}")
```

## TimezoneError

Raised when there are timezone-related issues.

```python
class TimezoneError(CalendarLinkError):
    """Raised when there are timezone-related issues."""
```

**Inherits from:** `CalendarLinkError`

**Usage:**
```python
from calendar_link.exceptions import TimezoneError

try:
    # Timezone operation
    pass
except TimezoneError as e:
    print(f"Timezone error: {e}")
```

## Error Handling Patterns

### Pattern 1: Specific Exception Handling

```python
from calendar_link.exceptions import (
    InvalidEventDataError,
    UnsupportedCalendarServiceError,
    TimezoneError
)

def process_event_safely(event, service):
    """Process event with specific error handling."""
    try:
        # Create event
        event = CalendarEvent(
            title=event.get("title", ""),
            start_time=event.get("start_time"),
            end_time=event.get("end_time")
        )
        
        # Generate link
        link = generator.generate_link(event, service)
        return link
        
    except InvalidEventDataError as e:
        print(f"Invalid event data: {e}")
        return None
    except UnsupportedCalendarServiceError as e:
        print(f"Unsupported service '{service}': {e}")
        return None
    except TimezoneError as e:
        print(f"Timezone error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Pattern 2: Error Collection

```python
def process_multiple_events(events, services):
    """Process multiple events, collecting all errors."""
    results = []
    errors = []
    
    for i, event_data in enumerate(events):
        try:
            event = CalendarEvent.from_dict(event_data)
            event_links = {}
            
            for service in services:
                try:
                    link = generator.generate_link(event, service)
                    event_links[service] = link
                except UnsupportedCalendarServiceError as e:
                    errors.append(f"Event {i+1}, Service {service}: {e}")
                    event_links[service] = f"Error: {str(e)}"
            
            results.append(event_links)
            
        except InvalidEventDataError as e:
            errors.append(f"Event {i+1}: {e}")
            results.append(None)
    
    return results, errors
```

### Pattern 3: Fallback Strategy

```python
def generate_link_with_fallback(event, preferred_service, fallback_services=None):
    """Generate link with fallback to other services."""
    if fallback_services is None:
        fallback_services = ["google", "apple", "outlook"]
    
    # Try preferred service first
    try:
        return generator.generate_link(event, preferred_service)
    except UnsupportedCalendarServiceError:
        print(f"Service '{preferred_service}' not supported, trying fallbacks...")
    
    # Try fallback services
    for service in fallback_services:
        try:
            return generator.generate_link(event, service)
        except UnsupportedCalendarServiceError:
            continue
    
    # If all services fail, raise the last error
    raise UnsupportedCalendarServiceError(
        f"None of the services {[preferred_service] + fallback_services} are supported"
    )
```

## Debugging Exceptions

### 1. Enable Detailed Error Messages

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

try:
    event = CalendarEvent(title="", start_time=datetime(2024, 1, 15, 10, 0))
except InvalidEventDataError as e:
    logging.error(f"Event creation failed: {e}")
    logging.debug(f"Event data: title='', start_time={datetime(2024, 1, 15, 10, 0)}")
```

### 2. Check Exception Types

```python
def handle_calendar_error(error):
    """Handle different types of calendar errors."""
    if isinstance(error, InvalidEventDataError):
        print("Invalid event data - check your event properties")
    elif isinstance(error, UnsupportedCalendarServiceError):
        print("Unsupported service - check the service name")
    elif isinstance(error, TimezoneError):
        print("Timezone error - check your timezone settings")
    else:
        print(f"Unexpected error: {error}")

try:
    # Some operation
    pass
except CalendarLinkError as e:
    handle_calendar_error(e)
```

### 3. Validate Input Before Processing

```python
def validate_event_data(event_data):
    """Validate event data before creating CalendarEvent."""
    errors = []
    
    # Check required fields
    if not event_data.get("title", "").strip():
        errors.append("Event title is required")
    
    # Check time validity
    start_time = event_data.get("start_time")
    end_time = event_data.get("end_time")
    
    if start_time and end_time and start_time >= end_time:
        errors.append("Start time must be before end time")
    
    return errors

# Usage
event_data = {
    "title": "",
    "start_time": datetime(2024, 1, 15, 10, 0),
    "end_time": datetime(2024, 1, 15, 9, 0)  # Before start
}

errors = validate_event_data(event_data)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
else:
    # Create event
    event = CalendarEvent.from_dict(event_data)
```

## Best Practices

### 1. Always Handle Specific Exceptions

```python
# Good: Handle specific exceptions
try:
    event = CalendarEvent(title="Meeting", start_time=datetime(2024, 1, 15, 10, 0))
    link = generator.generate_link(event, "google")
except InvalidEventDataError as e:
    print(f"Invalid event: {e}")
except UnsupportedCalendarServiceError as e:
    print(f"Unsupported service: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# Avoid: Bare except
try:
    # Some operation
    pass
except:  # Too broad
    pass
```

### 2. Provide Context in Error Messages

```python
def create_event_with_context(title, start_time, end_time=None):
    """Create event with contextual error messages."""
    try:
        return CalendarEvent(title=title, start_time=start_time, end_time=end_time)
    except InvalidEventDataError as e:
        if not title or not title.strip():
            print(f"Error creating event: Title cannot be empty (provided: '{title}')")
        elif end_time and start_time >= end_time:
            print(f"Error creating event: Start time ({start_time}) must be before end time ({end_time})")
        else:
            print(f"Error creating event: {e}")
        return None
```

### 3. Use Type Hints for Better Error Prevention

```python
from typing import Optional
from datetime import datetime

def create_event_safely(
    title: str,
    start_time: datetime,
    end_time: Optional[datetime] = None
) -> Optional[CalendarEvent]:
    """Create event with type safety."""
    try:
        return CalendarEvent(title=title, start_time=start_time, end_time=end_time)
    except InvalidEventDataError as e:
        print(f"Failed to create event: {e}")
        return None
```

## Related

- [CalendarEvent](calendar-event.md) - Event data model
- [CalendarGenerator](calendar-generator.md) - Link generation
- [Utilities](utils.md) - Helper functions 