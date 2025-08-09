# Error Handling

Learn how to handle errors and exceptions in the Calendar Link Generator.

## Overview

The Calendar Link Generator provides comprehensive error handling with custom exceptions to help you identify and resolve issues quickly.

## Exception Types

### CalendarLinkError

Base exception for all calendar link errors.

```python
from calendar_link.exceptions import CalendarLinkError

try:
    # Some operation
    pass
except CalendarLinkError as e:
    print(f"Calendar error: {e}")
```

### InvalidEventDataError

Raised when event data is invalid.

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

### UnsupportedCalendarServiceError

Raised when an unsupported calendar service is requested.

```python
from calendar_link.exceptions import UnsupportedCalendarServiceError

try:
    link = generator.generate_link(event, "invalid_service")
except UnsupportedCalendarServiceError as e:
    print(f"Unsupported service: {e}")
    # Output: Unsupported service: invalid_service. 
    # Supported services: ['google', 'apple', 'yahoo', 'aol', 'outlook', 'office365', 'ics']
```

### TimezoneError

Raised when there are timezone-related issues.

```python
from calendar_link.exceptions import TimezoneError

try:
    # Timezone operation
    pass
except TimezoneError as e:
    print(f"Timezone error: {e}")
```

## Common Error Scenarios

### 1. Invalid Event Data

```python
from calendar_link.exceptions import InvalidEventDataError

def create_safe_event(title, start_time, end_time=None):
    """Create an event with error handling."""
    try:
        event = CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time
        )
        return event
    except InvalidEventDataError as e:
        print(f"Failed to create event: {e}")
        return None

# Test with invalid data
event = create_safe_event("", datetime(2024, 1, 15, 10, 0))
if event is None:
    print("Event creation failed")
```

### 2. Unsupported Calendar Service

```python
from calendar_link.exceptions import UnsupportedCalendarServiceError

def generate_safe_link(event, service):
    """Generate calendar link with error handling."""
    try:
        return generator.generate_link(event, service)
    except UnsupportedCalendarServiceError as e:
        print(f"Unsupported service '{service}': {e}")
        return None

# Test with invalid service
link = generate_safe_link(event, "invalid_service")
if link is None:
    print("Link generation failed")
```

### 3. Timezone Issues

```python
from calendar_link.utils import get_timezone_offset

def validate_timezone(timezone):
    """Validate timezone and return offset."""
    try:
        offset = get_timezone_offset(timezone)
        return offset
    except Exception as e:
        print(f"Invalid timezone '{timezone}': {e}")
        return None

# Test timezone validation
offset = validate_timezone("Invalid/Timezone")
if offset is None:
    print("Using default timezone")
```

## Error Handling Patterns

### Pattern 1: Try-Catch with Fallback

```python
def generate_link_with_fallback(event, preferred_service, fallback_service="google"):
    """Generate link with fallback to another service."""
    try:
        return generator.generate_link(event, preferred_service)
    except UnsupportedCalendarServiceError:
        print(f"Service '{preferred_service}' not supported, using '{fallback_service}'")
        return generator.generate_link(event, fallback_service)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
link = generate_link_with_fallback(event, "invalid_service", "google")
```

### Pattern 2: Batch Processing with Error Collection

```python
def generate_links_for_events(events, services):
    """Generate links for multiple events, collecting errors."""
    results = {}
    errors = []
    
    for i, event in enumerate(events):
        event_links = {}
        for service in services:
            try:
                link = generator.generate_link(event, service)
                event_links[service] = link
            except Exception as e:
                error_msg = f"Event {i+1}, Service {service}: {e}"
                errors.append(error_msg)
                event_links[service] = f"Error: {str(e)}"
        
        results[f"event_{i+1}"] = event_links
    
    return results, errors

# Usage
events = [
    CalendarEvent(title="Meeting 1", start_time=datetime(2024, 1, 15, 10, 0)),
    CalendarEvent(title="Meeting 2", start_time=datetime(2024, 1, 15, 14, 0))
]

services = ["google", "apple", "invalid_service"]
results, errors = generate_links_for_events(events, services)

if errors:
    print("Errors encountered:")
    for error in errors:
        print(f"  - {error}")
```

### Pattern 3: Validation Before Processing

```python
def validate_event_before_processing(event):
    """Validate event before generating links."""
    errors = []
    
    # Check required fields
    if not event.title or not event.title.strip():
        errors.append("Event title is required")
    
    # Check time validity
    if event.start_time >= event.end_time:
        errors.append("Start time must be before end time")
    
    # Check all-day event validity
    if event.all_day and (event.start_time.hour != 0 or event.end_time.hour != 0):
        errors.append("All-day events should have 00:00 as time")
    
    return errors

def process_event_safely(event):
    """Process event with validation."""
    errors = validate_event_before_processing(event)
    
    if errors:
        print("Event validation failed:")
        for error in errors:
            print(f"  - {error}")
        return None
    
    # Generate links
    try:
        all_links = generator.generate_all_links(event)
        return all_links
    except Exception as e:
        print(f"Link generation failed: {e}")
        return None

# Usage
event = CalendarEvent(
    title="",  # Invalid: empty title
    start_time=datetime(2024, 1, 15, 10, 0)
)

links = process_event_safely(event)
if links is None:
    print("Event processing failed")
```

## Debugging Tips

### 1. Enable Detailed Error Messages

```python
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# This will show more detailed error information
try:
    event = CalendarEvent(title="", start_time=datetime(2024, 1, 15, 10, 0))
except InvalidEventDataError as e:
    logging.error(f"Event creation failed: {e}")
```

### 2. Check Event Properties

```python
def debug_event(event):
    """Debug event properties."""
    print(f"Title: '{event.title}'")
    print(f"Start time: {event.start_time}")
    print(f"End time: {event.end_time}")
    print(f"All day: {event.all_day}")
    print(f"Timezone: {event.timezone}")
    print(f"Attendees: {event.attendees}")

# Usage
event = CalendarEvent(
    title="Test Meeting",
    start_time=datetime(2024, 1, 15, 10, 0)
)

debug_event(event)
```

### 3. Validate Service Support

```python
def check_service_support(service):
    """Check if a service is supported."""
    supported_services = generator.get_supported_services()
    
    if service.lower() in [s.lower() for s in supported_services.keys()]:
        return True
    else:
        print(f"Service '{service}' not supported")
        print(f"Supported services: {list(supported_services.keys())}")
        return False

# Usage
if check_service_support("google"):
    link = generator.generate_link(event, "google")
```

## Best Practices

### 1. Always Handle Exceptions

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

### 2. Provide Meaningful Error Messages

```python
def create_event_with_validation(title, start_time, end_time=None):
    """Create event with detailed error messages."""
    try:
        return CalendarEvent(title=title, start_time=start_time, end_time=end_time)
    except InvalidEventDataError as e:
        if not title or not title.strip():
            print("Error: Event title cannot be empty")
        elif end_time and start_time >= end_time:
            print("Error: Start time must be before end time")
        else:
            print(f"Error: {e}")
        return None
```

### 3. Use Type Hints for Better Error Prevention

```python
from typing import Optional, List
from datetime import datetime

def create_event_safely(
    title: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    attendees: Optional[List[str]] = None
) -> Optional[CalendarEvent]:
    """Create event with type safety."""
    try:
        return CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees or []
        )
    except InvalidEventDataError as e:
        print(f"Failed to create event: {e}")
        return None
```

### 4. Log Errors for Debugging

```python
import logging

logger = logging.getLogger(__name__)

def process_events_with_logging(events):
    """Process events with error logging."""
    results = []
    
    for i, event in enumerate(events):
        try:
            links = generator.generate_all_links(event)
            results.append(links)
        except Exception as e:
            logger.error(f"Failed to process event {i+1}: {e}")
            results.append(None)
    
    return results
```

## Next Steps

- [Calendar Events](calendar-events.md) - Learn about event creation
- [Calendar Generator](calendar-generator.md) - Generate calendar links
- [Timezone Handling](timezone-handling.md) - Handle timezone issues
- [API Reference](../api/exceptions.md) - Complete exception documentation 