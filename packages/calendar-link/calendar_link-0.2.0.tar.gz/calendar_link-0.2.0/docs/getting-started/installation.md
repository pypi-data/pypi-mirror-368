# Installation

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation Methods

### From PyPI (Recommended)

```bash
pip install calendar-link
```

### From Source

```bash
# Clone the repository
git clone https://github.com/nneji123/calendar-link.git
cd calendar-link

# Install in development mode
pip install -e .
```

### Development Installation

For development and testing:

```bash
# Clone the repository
git clone https://github.com/nneji123/calendar-link.git
cd calendar-link

# Install with development dependencies
pip install -e ".[dev]"
```

## Dependencies

The package automatically installs the following dependencies:

- **ical** (>=11.0.0): Python iCalendar implementation
- **python-dateutil** (>=2.8.2): Date utilities
- **pytz** (>=2023.3): Timezone handling

## Verification

To verify the installation, run:

```python
from calendar_link import CalendarEvent, CalendarGenerator
print("Calendar Link Generator installed successfully!")
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the package
pip install calendar-link
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're using Python 3.8 or higher
2. **Permission Error**: Use `pip install --user calendar-link` or activate a virtual environment
3. **Dependency Conflicts**: Try installing in a fresh virtual environment

### Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/nneji123/calendar-link/issues)
2. Create a new issue with details about your environment
3. Join our [Discussions](https://github.com/nneji123/calendar-link/discussions)

## Next Steps

After installation, check out:

- [Quick Start Guide](quick-start.md) - Get up and running quickly
- [Basic Usage](basic-usage.md) - Learn the fundamentals
- [API Reference](../api/calendar-event.md) - Complete documentation 