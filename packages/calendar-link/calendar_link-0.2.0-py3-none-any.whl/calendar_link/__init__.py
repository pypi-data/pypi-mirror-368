"""
Calendar Link Generator

A Python package for generating calendar links and ICS files for various calendar services
including Google Calendar, Apple Calendar, Yahoo Calendar, AOL Calendar, and Microsoft 365.
"""

from .calendar_event import CalendarEvent
from .calendar_generator import CalendarGenerator
from .exceptions import CalendarLinkError

__version__ = "0.1.0"
__author__ = "Calendar Link Generator"
__all__ = ["CalendarEvent", "CalendarGenerator", "CalendarLinkError"] 