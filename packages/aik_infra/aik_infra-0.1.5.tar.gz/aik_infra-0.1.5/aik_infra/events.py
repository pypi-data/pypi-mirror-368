"""
Event definitions for AIKademiya platform
Implements Event-Driven Architecture with Kafka
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class EventType(str, Enum):
    # User Events
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    USER_SUBSCRIPTION_CHANGED = "user.subscription_changed"
    
    # Learning Events
    TRACK_GENERATION_REQUESTED = "learning.track_generation_requested"
    TRACK_GENERATION_COMPLETED = "learning.track_generation_completed"
    TRACK_GENERATION_FAILED = "learning.track_generation_failed"
    LESSON_STARTED = "learning.lesson_started"
    LESSON_COMPLETED = "learning.lesson_completed"
    MODULE_COMPLETED = "learning.module_completed"
    TRACK_COMPLETED = "learning.track_completed"
    
    # AI Agent Events
    AI_GENERATION_STARTED = "ai.generation_started"
    AI_GENERATION_COMPLETED = "ai.generation_completed"
    AI_GENERATION_FAILED = "ai.generation_failed"
    AI_FEEDBACK_RECEIVED = "ai.feedback_received"
    
    # Notification Events
    NOTIFICATION_REQUESTED = "notification.requested"
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"


class BaseEvent(BaseModel):
    """Base event class"""
    event_type: EventType
    event_id: str
    timestamp: datetime
    user_id: Optional[int] = None
    correlation_id: Optional[str] = None
    source_service: str
    data: Dict[str, Any]


class UserRegisteredEvent(BaseEvent):
    """Событие регистрации пользователя"""
    event_type: EventType = EventType.USER_REGISTERED


class TrackGenerationRequestedEvent(BaseEvent):
    """Событие запроса генерации трека"""
    event_type: EventType = EventType.TRACK_GENERATION_REQUESTED


class TrackGenerationCompletedEvent(BaseEvent):
    """Событие завершения генерации трека"""
    event_type: EventType = EventType.TRACK_GENERATION_COMPLETED


class LessonCompletedEvent(BaseEvent):
    """Событие завершения урока"""
    event_type: EventType = EventType.LESSON_COMPLETED


class NotificationRequestedEvent(BaseEvent):
    """Событие запроса уведомления"""
    event_type: EventType = EventType.NOTIFICATION_REQUESTED