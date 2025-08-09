# Supported Services

Detailed information about each supported calendar service.

## Google Calendar

**Method:** `"google"`  
**URL Format:** `https://calendar.google.com/calendar/render?...`

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ✅ Attendees (comma-separated)
- ✅ Timezone support

### Example
```python
google_link = generator.generate_link(event, "google")
# https://calendar.google.com/calendar/render?action=TEMPLATE&text=Team+Meeting&dates=20240115T100000Z/20240115T110000Z&details=Weekly+team+sync&location=Conference+Room+A&add=john%40example.com%2Cjane%40example.com
```

## Apple Calendar

**Method:** `"apple"`  
**URL Format:** `webcal://calendar.apple.com/event?...`

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported by Apple Calendar URLs)

### Example
```python
apple_link = generator.generate_link(event, "apple")
# webcal://calendar.apple.com/event?title=Team%20Meeting&start=2024-01-15T10:00:00&end=2024-01-15T11:00:00&description=Weekly%20team%20sync&location=Conference%20Room%20A
```

## Yahoo Calendar

**Method:** `"yahoo"`  
**URL Format:** `https://calendar.yahoo.com/?...`

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported)

### Example
```python
yahoo_link = generator.generate_link(event, "yahoo")
# https://calendar.yahoo.com/?v=60&title=Team+Meeting&st=20240115T100000Z&et=20240115T110000Z&desc=Weekly+team+sync&in_loc=Conference+Room+A
```

## AOL Calendar

**Method:** `"aol"`  
**URL Format:** `https://calendar.aol.com/?...`

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported)

### Example
```python
aol_link = generator.generate_link(event, "aol")
# https://calendar.aol.com/?v=60&title=Team+Meeting&st=20240115T100000Z&et=20240115T110000Z&desc=Weekly+team+sync&in_loc=Conference+Room+A
```

## Microsoft Outlook

**Method:** `"outlook"`  
**URL Format:** `https://outlook.live.com/calendar/0/...`

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported in URL format)

### Example
```python
outlook_link = generator.generate_link(event, "outlook")
# https://outlook.live.com/calendar/0/path=%2Fcalendar%2Faction%2Fcompose&rru=addevent&subject=Team+Meeting&startdt=2024-01-15T10%3A00%3A00&enddt=2024-01-15T11%3A00%3A00&body=Weekly+team+sync&location=Conference+Room+A
```

## Microsoft 365

**Method:** `"office365"`  
**URL Format:** `https://outlook.live.com/calendar/0/...`

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ❌ Attendees (not supported in URL format)

### Example
```python
office365_link = generator.generate_link(event, "office365")
# Same format as Outlook
```

## ICS File

**Method:** `"ics"`  
**Format:** Standard iCalendar format

### Features
- ✅ Event title and times
- ✅ Description
- ✅ Location
- ✅ Attendees
- ✅ Full iCalendar support
- ✅ Compatible with all calendar applications

### Example
```python
ics_content = generator.generate_ics(event)
# BEGIN:VCALENDAR
# VERSION:2.0
# PRODID:-//Calendar Link Generator//EN
# CALSCALE:GREGORIAN
# METHOD:PUBLISH
# BEGIN:VEVENT
# UID:Team_Meeting_20240115100000
# DTSTAMP:20240115T100000Z
# DTSTART:20240115T100000Z
# DTEND:20240115T110000Z
# SUMMARY:Team Meeting
# DESCRIPTION:Weekly team sync meeting
# LOCATION:Conference Room A
# ATTENDEE:john@example.com
# ATTENDEE:jane@example.com
# END:VEVENT
# END:VCALENDAR
```

## Service Comparison

| Feature | Google | Apple | Yahoo | AOL | Outlook | Office 365 | ICS |
|---------|--------|-------|-------|-----|---------|------------|-----|
| Event Title | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Start/End Time | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Description | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Location | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Attendees | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Timezone Support | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| All-Day Events | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## Best Practices by Service

### Google Calendar
- Best for events with attendees
- Supports all features
- Most widely used

### Apple Calendar
- Good for iOS/macOS users
- Clean URL format
- No attendee support

### Microsoft Services
- Good for enterprise users
- Outlook and Office 365 compatible
- No attendee support in URLs

### Yahoo/AOL Calendar
- Legacy services
- Basic feature support
- Good for older systems

### ICS Files
- Maximum compatibility
- Works with all calendar applications
- Best for universal sharing 