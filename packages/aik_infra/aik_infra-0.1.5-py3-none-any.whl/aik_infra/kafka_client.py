"""
Kafka client for event-driven communication between services
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
from uuid import uuid4
from datetime import datetime

import aiokafka
from pydantic import BaseModel

from aik_infra.events import BaseEvent, EventType

logger = logging.getLogger(__name__)


class KafkaClient:
    """Асинхронный Kafka клиент для публикации и подписки на события"""
    
    def __init__(self, bootstrap_servers: str, service_name: str):
        self.bootstrap_servers = bootstrap_servers
        self.service_name = service_name
        self.producer: Optional[aiokafka.AIOKafkaProducer] = None
        self.consumer: Optional[aiokafka.AIOKafkaConsumer] = None
        self.event_handlers: Dict[EventType, Callable] = {}
        self._running = False
    
    async def start_producer(self):
        """Запуск продюсера"""
        self.producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        await self.producer.start()
        logger.info(f"Kafka producer started for service: {self.service_name}")
    
    async def start_consumer(self, topics: list[str], group_id: str):
        """Запуск консюмера"""
        self.consumer = aiokafka.AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest'
        )
        await self.consumer.start()
        logger.info(f"Kafka consumer started for service: {self.service_name}, topics: {topics}")
    
    async def publish_event(self, event: BaseEvent, topic: str = None):
        """Публикация события"""
        if not self.producer:
            await self.start_producer()
        
        # Определяем топик на основе типа события, если не указан
        if topic is None:
            topic = self._get_topic_by_event_type(event.event_type)
        
        # Устанавливаем сервис-источник
        event.source_service = self.service_name
        event.timestamp = datetime.utcnow()
        
        try:
            await self.producer.send(
                topic,
                value=event.dict(),
                key=str(event.user_id) if event.user_id else None
            )
            logger.info(f"Event published: {event.event_type} to topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            raise
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Регистрация обработчика событий"""
        self.event_handlers[event_type] = handler
        logger.info(f"Handler registered for event type: {event_type}")
    
    async def start_listening(self):
        """Запуск прослушивания событий"""
        if not self.consumer:
            raise ValueError("Consumer not started. Call start_consumer() first.")
        
        self._running = True
        logger.info(f"Started listening for events in service: {self.service_name}")
        
        try:
            async for message in self.consumer:
                if not self._running:
                    break
                
                try:
                    event_data = message.value
                    event_type = EventType(event_data.get('event_type'))
                    
                    if event_type in self.event_handlers:
                        logger.info(f"Processing event: {event_type}")
                        await self.event_handlers[event_type](event_data)
                    else:
                        logger.debug(f"No handler for event type: {event_type}")
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # В production здесь должна быть логика retry/dead letter queue
        except Exception as e:
            logger.error(f"Error in event listener: {e}")
            raise
    
    async def stop(self):
        """Остановка клиента"""
        self._running = False
        
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
        
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")
    
    def _get_topic_by_event_type(self, event_type: EventType) -> str:
        """Определение топика по типу события"""
        if event_type.value.startswith('user.'):
            return 'user-events'
        elif event_type.value.startswith('learning.'):
            return 'learning-events'
        elif event_type.value.startswith('ai.'):
            return 'ai-events'
        elif event_type.value.startswith('notification.'):
            return 'notification-events'
        else:
            return 'general-events'


class EventPublisher:
    """Упрощенный интерфейс для публикации событий"""
    
    def __init__(self, kafka_client: KafkaClient):
        self.kafka_client = kafka_client
    
    async def publish_user_registered(self, user_id: int, user_data: Dict[str, Any]):
        """Публикация события регистрации пользователя"""
        from aik_infra.events import UserRegisteredEvent
        
        event = UserRegisteredEvent(
            event_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            source_service=self.kafka_client.service_name,
            data=user_data
        )
        
        await self.kafka_client.publish_event(event)
    
    async def publish_track_generation_requested(
        self, 
        user_id: int, 
        track_data: Dict[str, Any],
        correlation_id: str = None
    ):
        """Публикация события запроса генерации трека"""
        from aik_infra.events import TrackGenerationRequestedEvent
        
        event = TrackGenerationRequestedEvent(
            event_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            correlation_id=correlation_id or str(uuid4()),
            source_service=self.kafka_client.service_name,
            data=track_data
        )
        
        await self.kafka_client.publish_event(event)
    
    async def publish_notification_requested(
        self, 
        user_id: int, 
        notification_data: Dict[str, Any]
    ):
        """Публикация события запроса уведомления"""
        from aik_infra.events import NotificationRequestedEvent
        
        event = NotificationRequestedEvent(
            event_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            source_service=self.kafka_client.service_name,
            data=notification_data
        )
        
        await self.kafka_client.publish_event(event)