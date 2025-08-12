"""
Mentorstec - Centralized event logging and data platform with Repository Pattern
"""

__version__ = "0.1.3"

from .eventhub import (
    EventHubClient,
    capture_errors,
    send_error,
    send_event,
    setup_global_hub,
)
from .repository.eventhub_repository import EventHubRepository

__all__ = [
    "EventHubClient",
    "EventHubRepository",
    "setup_global_hub",
    "send_event",
    "send_error",
    "capture_errors",
]

# Optional imports with graceful fallback
try:
    from .dremio import Dremio  # noqa: F401
    from .repository.dremio_repository import DremioRepository  # noqa: F401

    __all__.extend(["Dremio", "DremioRepository"])
except ImportError:
    pass

try:
    from .powerbi import PowerBi  # noqa: F401
    from .repository.powerbi_repository import PowerBiRepository  # noqa: F401

    __all__.extend(["PowerBi", "PowerBiRepository"])
except ImportError:
    pass
