"""
Mentorstec EventHub - Módulo independente para centralized event logging

Estrutura usando Repository Pattern:
- EventHubRepository: Interface abstrata
- EventHubClient: Cliente principal para gerenciar eventos
- Funções globais: setup_global_hub, send_event, capture_errors
"""

from .event_hub import capture_errors, send_error, send_event, setup_global_hub
from .event_hub_client import EventHubClient

__all__ = [
    "EventHubClient",
    "setup_global_hub",
    "send_event",
    "send_error",
    "capture_errors",
]
