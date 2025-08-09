# Advanced Examples

Advanced usage patterns and complex scenarios.

## Batch Processing

### Process Multiple Events

```python
from datetime import datetime, timedelta
from calendar_link import CalendarEvent, CalendarGenerator

def create_recurring_events(base_date, title, start_hour, duration_hours, weeks=4):
    """Create weekly recurring events."""
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
weekly_meetings = create_recurring_events(
    base_date=base_date,
    title="Weekly Team Sync",
    start_hour=10,
    duration_hours=1,
    weeks=8
)

# Generate links for all events
generator = CalendarGenerator()
all_links = {}

for i, event in enumerate(weekly_meetings):
    event_links = generator.generate_all_links(event)
    all_links[f"week_{i+1}"] = event_links
```

### Batch Link Generation with Error Handling

```python
def generate_links_for_events(events, services=None):
    """Generate links for multiple events with error handling."""
    if services is None:
        services = ["google", "apple", "outlook"]
    
    generator = CalendarGenerator()
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

results, errors = generate_links_for_events(events)

if errors:
    print("Errors encountered:")
    for error in errors:
        print(f"  - {error}")
```

## Timezone Management

### Multi-TimeZone Event Creation

```python
import pytz
from datetime import datetime

def create_timezone_aware_events():
    """Create events in different timezones."""
    events = {}
    
    # Same time in different timezones
    base_time = datetime(2024, 1, 15, 10, 0)
    timezones = ["America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]
    
    for tz_name in timezones:
        tz_obj = pytz.timezone(tz_name)
        local_time = tz_obj.localize(base_time)
        
        event = CalendarEvent(
            title=f"Meeting ({tz_name})",
            start_time=local_time,
            timezone=tz_name
        )
        events[tz_name] = event
    
    return events

# Create events
tz_events = create_timezone_aware_events()

# Generate links for each timezone
generator = CalendarGenerator()
for tz_name, event in tz_events.items():
    google_link = generator.generate_link(event, "google")
    print(f"{tz_name}: {google_link}")
```

### Timezone Conversion Utility

```python
def convert_event_timezone(event, target_timezone):
    """Convert event to different timezone."""
    import pytz
    
    # Get source timezone
    source_tz = pytz.timezone(event.timezone or "UTC")
    
    # Convert times
    start_time = event.start_time.astimezone(pytz.timezone(target_timezone))
    end_time = event.end_time.astimezone(pytz.timezone(target_timezone))
    
    # Create new event
    converted_event = CalendarEvent(
        title=event.title,
        start_time=start_time,
        end_time=end_time,
        description=event.description,
        location=event.location,
        attendees=event.attendees,
        all_day=event.all_day,
        timezone=target_timezone
    )
    
    return converted_event

# Usage
ny_event = CalendarEvent(
    title="NY Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    timezone="America/New_York"
)

# Convert to LA time
la_event = convert_event_timezone(ny_event, "America/Los_Angeles")
```

## Advanced Event Patterns

### Conference Event

```python
def create_conference_event():
    """Create a multi-day conference event."""
    conference = CalendarEvent(
        title="Annual Developer Conference",
        start_time=datetime(2024, 1, 15, 9, 0),
        end_time=datetime(2024, 1, 17, 17, 0),
        description="Join us for three days of talks, workshops, and networking",
        location="Convention Center, Downtown",
        attendees=["speakers@conference.com", "organizers@conference.com"]
    )
    
    return conference

# Generate all links for conference
conference = create_conference_event()
generator = CalendarGenerator()
conference_links = generator.generate_all_links(conference)
```

### Recurring Event with Exceptions

```python
from datetime import datetime, timedelta
import calendar

def create_recurring_event_with_exceptions(base_date, title, start_hour, duration_hours, 
                                         exceptions=None, months=3):
    """Create recurring monthly events with exception dates."""
    if exceptions is None:
        exceptions = []
    
    events = []
    current_date = base_date
    
    for month in range(months):
        # Get the same day of month
        if current_date.day > 28:
            # Handle month end edge cases
            next_month = current_date.replace(day=1) + timedelta(days=32)
            current_date = next_month.replace(day=base_date.day)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        
        # Skip if this date is in exceptions
        if current_date.date() in exceptions:
            continue
        
        start_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=start_hour)
        end_time = start_time + timedelta(hours=duration_hours)
        
        event = CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time
        )
        events.append(event)
    
    return events

# Create monthly meetings with holiday exceptions
base_date = datetime(2024, 1, 15)
exceptions = [
    datetime(2024, 2, 15).date(),  # Skip February (holiday)
    datetime(2024, 3, 15).date()   # Skip March (holiday)
]

monthly_meetings = create_recurring_event_with_exceptions(
    base_date=base_date,
    title="Monthly Board Meeting",
    start_hour=14,
    duration_hours=2,
    exceptions=exceptions,
    months=6
)
```

## Data Integration

### CSV to Calendar Events

```python
import csv
from datetime import datetime
from calendar_link import CalendarEvent

def create_events_from_csv(csv_file):
    """Create events from CSV file."""
    events = []
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                # Parse datetime
                start_time = datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M')
                end_time = datetime.strptime(row['end_time'], '%Y-%m-%d %H:%M')
                
                # Parse attendees
                attendees = []
                if row.get('attendees'):
                    attendees = [email.strip() for email in row['attendees'].split(',')]
                
                event = CalendarEvent(
                    title=row['title'],
                    start_time=start_time,
                    end_time=end_time,
                    description=row.get('description', ''),
                    location=row.get('location', ''),
                    attendees=attendees
                )
                events.append(event)
                
            except Exception as e:
                print(f"Error processing row {row}: {e}")
                continue
    
    return events

# Example CSV format:
# title,start_time,end_time,description,location,attendees
# Team Meeting,2024-01-15 10:00,2024-01-15 11:00,Weekly sync,Conference Room A,john@example.com,jane@example.com
```

### JSON to Calendar Events

```python
import json
from calendar_link import CalendarEvent

def create_events_from_json(json_file):
    """Create events from JSON file."""
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    events = []
    
    for event_data in data['events']:
        try:
            # Parse datetime strings
            start_time = datetime.fromisoformat(event_data['start_time'])
            end_time = datetime.fromisoformat(event_data['end_time'])
            
            event = CalendarEvent(
                title=event_data['title'],
                start_time=start_time,
                end_time=end_time,
                description=event_data.get('description', ''),
                location=event_data.get('location', ''),
                attendees=event_data.get('attendees', []),
                all_day=event_data.get('all_day', False)
            )
            events.append(event)
            
        except Exception as e:
            print(f"Error processing event {event_data.get('title', 'Unknown')}: {e}")
            continue
    
    return events

# Example JSON format:
# {
#   "events": [
#     {
#       "title": "Team Meeting",
#       "start_time": "2024-01-15T10:00:00",
#       "end_time": "2024-01-15T11:00:00",
#       "description": "Weekly team sync",
#       "location": "Conference Room A",
#       "attendees": ["john@example.com", "jane@example.com"],
#       "all_day": false
#     }
#   ]
# }
```

## Advanced ICS Generation

### Custom ICS with Multiple Events

```python
from ical.calendar import Calendar
from ical.event import Event as IcalEvent

def create_calendar_with_multiple_events(events):
    """Create ICS calendar with multiple events."""
    calendar = Calendar()
    
    for event in events:
        ical_event = IcalEvent(
            summary=event.title,
            dtstart=event.start_time,
            dtend=event.end_time,
            description=event.description,
            location=event.location,
        )
        
        # Add attendees
        for attendee in event.attendees:
            ical_event.attendees.append(attendee)
        
        calendar.events.append(ical_event)
    
    return str(calendar)

# Create multiple events
events = [
    CalendarEvent(title="Meeting 1", start_time=datetime(2024, 1, 15, 10, 0)),
    CalendarEvent(title="Meeting 2", start_time=datetime(2024, 1, 15, 14, 0)),
    CalendarEvent(title="Meeting 3", start_time=datetime(2024, 1, 16, 9, 0))
]

# Generate ICS with all events
ics_content = create_calendar_with_multiple_events(events)

# Save to file
with open("all_meetings.ics", "w") as f:
    f.write(ics_content)
```

## Service-Specific Optimizations

### Google Calendar Optimization

```python
def optimize_for_google_calendar(event):
    """Optimize event for Google Calendar features."""
    # Google Calendar supports the most features
    optimized_event = CalendarEvent(
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        description=event.description,
        location=event.location,
        attendees=event.attendees,  # Google supports attendees
        all_day=event.all_day,
        timezone=event.timezone
    )
    
    return optimized_event

def generate_google_optimized_links(events):
    """Generate Google Calendar links for multiple events."""
    generator = CalendarGenerator()
    links = []
    
    for event in events:
        optimized_event = optimize_for_google_calendar(event)
        link = generator.generate_link(optimized_event, "google")
        links.append(link)
    
    return links
```

### Universal ICS Generation

```python
def generate_universal_ics(events):
    """Generate ICS files for maximum compatibility."""
    generator = CalendarGenerator()
    ics_files = []
    
    for event in events:
        ics_content = generator.generate_ics(event)
        ics_files.append(ics_content)
    
    return ics_files

def save_ics_files(events, base_filename="event"):
    """Save individual ICS files for each event."""
    generator = CalendarGenerator()
    
    for i, event in enumerate(events):
        ics_content = generator.generate_ics(event)
        filename = f"{base_filename}_{i+1}.ics"
        
        with open(filename, "w") as f:
            f.write(ics_content)
        
        print(f"Saved {filename}")
```

## Error Recovery Patterns

### Retry with Fallback Services

```python
def generate_link_with_retry(event, preferred_services, max_retries=3):
    """Generate link with retry and fallback logic."""
    generator = CalendarGenerator()
    
    for attempt in range(max_retries):
        for service in preferred_services:
            try:
                link = generator.generate_link(event, service)
                return link
            except Exception as e:
                print(f"Attempt {attempt + 1}: Failed to generate {service} link: {e}")
                continue
        
        if attempt < max_retries - 1:
            print(f"Retrying... (attempt {attempt + 2})")
    
    # If all attempts fail, try ICS
    try:
        ics_content = generator.generate_ics(event)
        return f"ICS file content (fallback): {ics_content[:100]}..."
    except Exception as e:
        raise Exception(f"All link generation attempts failed: {e}")

# Usage
preferred_services = ["google", "apple", "outlook"]
link = generate_link_with_retry(event, preferred_services)
```

## Performance Optimization

### Batch Processing with Caching

```python
from functools import lru_cache

class CachedCalendarGenerator:
    """Calendar generator with caching for performance."""
    
    def __init__(self):
        self.generator = CalendarGenerator()
        self._link_cache = {}
    
    @lru_cache(maxsize=1000)
    def generate_cached_link(self, event_hash, service):
        """Generate link with caching."""
        # Reconstruct event from hash (simplified)
        # In practice, you'd need a proper serialization method
        return self.generator.generate_link(event_hash, service)
    
    def generate_all_links_cached(self, event):
        """Generate all links with caching."""
        event_hash = hash(str(event.to_dict()))
        
        all_links = {}
        for service in self.generator.get_supported_services():
            link = self.generate_cached_link(event_hash, service)
            all_links[service] = link
        
        return all_links

# Usage
cached_generator = CachedCalendarGenerator()
links = cached_generator.generate_all_links_cached(event)
```

## Next Steps

- [Integration Examples](integration-examples.md) - Real-world integrations
- [User Guide](../user-guide/calendar-events.md) - Detailed event creation guide
- [API Reference](../api/calendar-generator.md) - Complete API documentation 