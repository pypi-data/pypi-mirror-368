# Integration Examples

Real-world integration examples and use cases.

## Web Application Integration

### Flask Web App

```python
from flask import Flask, request, jsonify
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

app = Flask(__name__)
generator = CalendarGenerator()

@app.route('/generate-calendar-link', methods=['POST'])
def generate_calendar_link():
    """Generate calendar link from web form data."""
    try:
        data = request.get_json()
        
        # Parse datetime
        start_time = datetime.fromisoformat(data['start_time'])
        end_time = datetime.fromisoformat(data['end_time'])
        
        # Create event
        event = CalendarEvent(
            title=data['title'],
            start_time=start_time,
            end_time=end_time,
            description=data.get('description', ''),
            location=data.get('location', ''),
            attendees=data.get('attendees', [])
        )
        
        # Generate links
        service = data.get('service', 'google')
        link = generator.generate_link(event, service)
        
        return jsonify({
            'success': True,
            'link': link,
            'service': service
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/generate-all-links', methods=['POST'])
def generate_all_links():
    """Generate links for all supported services."""
    try:
        data = request.get_json()
        
        # Create event
        event = CalendarEvent(
            title=data['title'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            description=data.get('description', ''),
            location=data.get('location', ''),
            attendees=data.get('attendees', [])
        )
        
        # Generate all links
        all_links = generator.generate_all_links(event)
        
        return jsonify({
            'success': True,
            'links': all_links
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Integration

```python
# models.py
from django.db import models
from calendar_link import CalendarEvent, CalendarGenerator

class Meeting(models.Model):
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    attendees = models.JSONField(default=list)
    
    def to_calendar_event(self):
        """Convert to CalendarEvent."""
        return CalendarEvent(
            title=self.title,
            start_time=self.start_time,
            end_time=self.end_time,
            description=self.description,
            location=self.location,
            attendees=self.attendees
        )
    
    def generate_google_link(self):
        """Generate Google Calendar link."""
        generator = CalendarGenerator()
        event = self.to_calendar_event()
        return generator.generate_link(event, "google")
    
    def generate_all_links(self):
        """Generate links for all services."""
        generator = CalendarGenerator()
        event = self.to_calendar_event()
        return generator.generate_all_links(event)

# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Meeting

@csrf_exempt
def generate_calendar_link(request):
    """Generate calendar link for a meeting."""
    if request.method == 'POST':
        try:
            data = request.POST
            
            meeting = Meeting.objects.create(
                title=data['title'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                description=data.get('description', ''),
                location=data.get('location', ''),
                attendees=data.get('attendees', [])
            )
            
            service = data.get('service', 'google')
            link = meeting.generate_google_link()
            
            return JsonResponse({
                'success': True,
                'link': link,
                'meeting_id': meeting.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
```

## Email Integration

### Email with Calendar Links

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from calendar_link import CalendarEvent, CalendarGenerator

def send_meeting_invitation(recipients, event_data):
    """Send meeting invitation with calendar links."""
    # Create event
    event = CalendarEvent(
        title=event_data['title'],
        start_time=event_data['start_time'],
        end_time=event_data['end_time'],
        description=event_data.get('description', ''),
        location=event_data.get('location', ''),
        attendees=recipients
    )
    
    # Generate links
    generator = CalendarGenerator()
    all_links = generator.generate_all_links(event)
    
    # Create email
    msg = MIMEMultipart()
    msg['Subject'] = f"Meeting Invitation: {event.title}"
    msg['From'] = "organizer@example.com"
    msg['To'] = ", ".join(recipients)
    
    # Email body
    body = f"""
    Meeting: {event.title}
    Time: {event.start_time} - {event.end_time}
    Location: {event.location or 'TBD'}
    Description: {event.description or 'No description'}
    
    Calendar Links:
    """
    
    for service, link in all_links.items():
        body += f"\n{service.upper()}: {link}"
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('username', 'password')
        server.send_message(msg)

# Usage
event_data = {
    'title': 'Weekly Team Sync',
    'start_time': datetime(2024, 1, 15, 10, 0),
    'end_time': datetime(2024, 1, 15, 11, 0),
    'description': 'Weekly team status update',
    'location': 'Conference Room A'
}

recipients = ['john@example.com', 'jane@example.com']
send_meeting_invitation(recipients, event_data)
```

## API Integration

### REST API Service

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

app = FastAPI()
generator = CalendarGenerator()

class EventRequest(BaseModel):
    title: str
    start_time: str
    end_time: str
    description: str = ""
    location: str = ""
    attendees: list = []

class EventResponse(BaseModel):
    success: bool
    links: dict
    ics_content: str

@app.post("/api/calendar/generate-links", response_model=EventResponse)
async def generate_calendar_links(request: EventRequest):
    """Generate calendar links for an event."""
    try:
        # Parse datetime
        start_time = datetime.fromisoformat(request.start_time)
        end_time = datetime.fromisoformat(request.end_time)
        
        # Create event
        event = CalendarEvent(
            title=request.title,
            start_time=start_time,
            end_time=end_time,
            description=request.description,
            location=request.location,
            attendees=request.attendees
        )
        
        # Generate links
        all_links = generator.generate_all_links(event)
        ics_content = generator.generate_ics(event)
        
        return EventResponse(
            success=True,
            links=all_links,
            ics_content=ics_content
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/calendar/services")
async def get_supported_services():
    """Get list of supported calendar services."""
    services = generator.get_supported_services()
    return {"services": services}

@app.post("/api/calendar/validate-event")
async def validate_event(request: EventRequest):
    """Validate event data."""
    try:
        start_time = datetime.fromisoformat(request.start_time)
        end_time = datetime.fromisoformat(request.end_time)
        
        event = CalendarEvent(
            title=request.title,
            start_time=start_time,
            end_time=end_time,
            description=request.description,
            location=request.location,
            attendees=request.attendees
        )
        
        return {"valid": True, "event": event.to_dict()}
        
    except Exception as e:
        return {"valid": False, "error": str(e)}
```

## Database Integration

### SQLAlchemy Integration

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from calendar_link import CalendarEvent, CalendarGenerator

Base = declarative_base()

class CalendarEventModel(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    description = Column(Text)
    location = Column(String(200))
    attendees = Column(Text)  # JSON string
    
    def to_calendar_event(self):
        """Convert to CalendarEvent."""
        import json
        attendees = json.loads(self.attendees) if self.attendees else []
        
        return CalendarEvent(
            title=self.title,
            start_time=self.start_time,
            end_time=self.end_time,
            description=self.description,
            location=self.location,
            attendees=attendees
        )

# Database operations
engine = create_engine('sqlite:///calendar_events.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_event_to_db(event_data):
    """Save event to database."""
    session = Session()
    
    import json
    db_event = CalendarEventModel(
        title=event_data['title'],
        start_time=event_data['start_time'],
        end_time=event_data['end_time'],
        description=event_data.get('description', ''),
        location=event_data.get('location', ''),
        attendees=json.dumps(event_data.get('attendees', []))
    )
    
    session.add(db_event)
    session.commit()
    session.close()
    
    return db_event.id

def generate_links_from_db(event_id):
    """Generate calendar links for event in database."""
    session = Session()
    db_event = session.query(CalendarEventModel).filter_by(id=event_id).first()
    
    if not db_event:
        session.close()
        raise ValueError("Event not found")
    
    event = db_event.to_calendar_event()
    generator = CalendarGenerator()
    links = generator.generate_all_links(event)
    
    session.close()
    return links
```

## Mobile App Integration

### React Native Example

```javascript
// CalendarService.js
class CalendarService {
  static async generateCalendarLinks(eventData) {
    try {
      const response = await fetch('https://api.example.com/calendar/generate-links', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: eventData.title,
          start_time: eventData.startTime,
          end_time: eventData.endTime,
          description: eventData.description,
          location: eventData.location,
          attendees: eventData.attendees
        })
      });
      
      const result = await response.json();
      return result.links;
    } catch (error) {
      console.error('Error generating calendar links:', error);
      throw error;
    }
  }
  
  static openCalendarApp(link) {
    // Open calendar app with the generated link
    Linking.openURL(link);
  }
}

// Usage in React Native component
import React, { useState } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import CalendarService from './CalendarService';

const MeetingScreen = () => {
  const [links, setLinks] = useState(null);
  
  const generateLinks = async () => {
    try {
      const eventData = {
        title: 'Team Meeting',
        startTime: '2024-01-15T10:00:00',
        endTime: '2024-01-15T11:00:00',
        description: 'Weekly team sync',
        location: 'Conference Room A',
        attendees: ['john@example.com', 'jane@example.com']
      };
      
      const calendarLinks = await CalendarService.generateCalendarLinks(eventData);
      setLinks(calendarLinks);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate calendar links');
    }
  };
  
  const openGoogleCalendar = () => {
    if (links && links.google) {
      CalendarService.openCalendarApp(links.google);
    }
  };
  
  return (
    <View>
      <Button title="Generate Calendar Links" onPress={generateLinks} />
      {links && (
        <View>
          <Button title="Open Google Calendar" onPress={openGoogleCalendar} />
          <Text>Google: {links.google}</Text>
          <Text>Apple: {links.apple}</Text>
        </View>
      )}
    </View>
  );
};
```

## Slack Integration

### Slack Bot with Calendar Links

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from calendar_link import CalendarEvent, CalendarGenerator
import re

app = App(token="your-slack-token")
generator = CalendarGenerator()

@app.message(re.compile(r"create meeting (.+)"))
def handle_meeting_request(message, say, context):
    """Handle meeting creation requests in Slack."""
    try:
        # Parse meeting details from message
        meeting_text = context.matches[0]
        
        # Simple parsing (in practice, use NLP or structured input)
        parts = meeting_text.split(" at ")
        if len(parts) != 2:
            say("Please provide meeting details in format: 'create meeting [title] at [time]'")
            return
        
        title = parts[0].strip()
        time_str = parts[1].strip()
        
        # Parse time (simplified)
        from datetime import datetime, timedelta
        start_time = datetime.now() + timedelta(hours=1)  # Default to 1 hour from now
        end_time = start_time + timedelta(hours=1)
        
        # Create event
        event = CalendarEvent(
            title=title,
            start_time=start_time,
            end_time=end_time
        )
        
        # Generate links
        all_links = generator.generate_all_links(event)
        
        # Create Slack message with links
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Meeting Created: {title}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Google Calendar"
                        },
                        "url": all_links['google']
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Apple Calendar"
                        },
                        "url": all_links['apple']
                    }
                ]
            }
        ]
        
        say(blocks=blocks)
        
    except Exception as e:
        say(f"Error creating meeting: {str(e)}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, "your-app-token")
    handler.start()
```

## Next Steps

- [Basic Examples](basic-examples.md) - Simple usage examples
- [Advanced Examples](advanced-examples.md) - Complex patterns
- [User Guide](../user-guide/calendar-events.md) - Detailed documentation
- [API Reference](../api/calendar-generator.md) - Complete API documentation 