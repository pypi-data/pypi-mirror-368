# Calendar Link Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![PyPI](https://img.shields.io/badge/PyPI-v0.1.0-orange.svg)
![Codecov](https://img.shields.io/badge/Codecov-90%25-brightgreen.svg)

**Generate calendar links and ICS files for various calendar services**

[Installation](getting-started/installation.md){ .md-button .md-button--primary }
[Quick Start](getting-started/quick-start.md){ .md-button .md-button--secondary }
[API Reference](api/calendar-event.md){ .md-button .md-button--secondary }

</div>

---

## 🚀 Features

- **Multiple Calendar Services**: Support for Google Calendar, Apple Calendar, Yahoo Calendar, AOL Calendar, Microsoft Outlook, and Microsoft 365
- **ICS File Generation**: Create standard iCalendar files for universal compatibility
- **Timezone Support**: Full timezone handling with pytz integration
- **Event Validation**: Comprehensive validation and sanitization
- **Error Handling**: Custom exceptions for better debugging
- **Utility Functions**: Helper functions for common operations

## 📦 Supported Services

| Service | Status | Link Format |
|---------|--------|-------------|
| Google Calendar | ✅ | `https://calendar.google.com/...` |
| Apple Calendar | ✅ | `webcal://calendar.apple.com/...` |
| Yahoo Calendar | ✅ | `https://calendar.yahoo.com/...` |
| AOL Calendar | ✅ | `https://calendar.aol.com/...` |
| Microsoft Outlook | ✅ | `https://outlook.live.com/...` |
| Microsoft 365 | ✅ | `https://outlook.live.com/...` |
| ICS File | ✅ | Standard iCalendar format |

## 🎯 Quick Example

```python
from datetime import datetime
from calendar_link import CalendarEvent, CalendarGenerator

# Create an event
event = CalendarEvent(
    title="Team Meeting",
    start_time=datetime(2024, 1, 15, 10, 0),
    end_time=datetime(2024, 1, 15, 11, 0),
    description="Weekly team sync meeting",
    location="Conference Room A",
    attendees=["john@example.com", "jane@example.com"]
)

# Generate calendar links
generator = CalendarGenerator()

# Google Calendar link
google_link = generator.generate_link(event, "google")
print(f"Google Calendar: {google_link}")

# ICS file content
ics_content = generator.generate_ics(event)
print(f"ICS Content:\n{ics_content}")
```

## 🔧 Installation

```bash
pip install calendar-link
```

## 📚 Documentation

- **[Getting Started](getting-started/installation.md)**: Installation and basic setup
- **[User Guide](user-guide/calendar-events.md)**: Detailed usage instructions
- **[API Reference](api/calendar-event.md)**: Complete API documentation
- **[Examples](examples/basic-examples.md)**: Code examples and use cases
- **[Development](development/contributing.md)**: Contributing guidelines

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [License](about/license.md) file for details.

## 🙏 Acknowledgments

- [ical](https://github.com/allenporter/ical) - Python iCalendar implementation
- [python-dateutil](https://dateutil.readthedocs.io/) - Date utilities
- [pytz](https://pythonhosted.org/pytz/) - Timezone handling

---

<div align="center">

**Made with ❤️ by the Calendar Link Generator Team**

[GitHub](https://github.com/nneji123/calendar-link){ .md-button .md-button--primary }
[Issues](https://github.com/nneji123/calendar-link/issues){ .md-button .md-button--secondary }
[Discussions](https://github.com/nneji123/calendar-link/discussions){ .md-button .md-button--secondary }

</div> 