from dataclasses import dataclass
from typing import Optional


@dataclass
class NotificationEvent:
    event_type: str
    source_service: str
    data: dict
    timestamp: float
    correlation_id: Optional[str] = None
