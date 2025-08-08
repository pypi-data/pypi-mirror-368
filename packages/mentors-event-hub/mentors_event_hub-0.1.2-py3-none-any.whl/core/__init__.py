"""
Mentors Event Hub - Centralized event logging with Repository Pattern
"""

__version__ = "0.1.2"

from .event_hub import capture_errors, send_error, send_event, setup_global_hub
from .event_hub_client import EventHubClient
from .repository.event_repository import EventRepository

__all__ = [
    "EventHubClient",
    "EventRepository",
    "setup_global_hub",
    "send_event",
    "send_error",
    "capture_errors",
]
