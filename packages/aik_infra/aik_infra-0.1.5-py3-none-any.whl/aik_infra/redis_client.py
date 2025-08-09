"""
Redis client for pub/sub functionality
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, Callable, List
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for pub/sub operations"""
    
    def __init__(self, host: str = None, port: int = None, db: int = 0):
        self.host = host or os.getenv("REDIS_HOST", "redis")
        self.port = port or int(os.getenv("REDIS_PORT", "6379"))
        self.db = db
        self.redis: Optional[Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self._subscribers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
        self._running = False
        logger.info("Disconnected from Redis")
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to Redis channel"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        try:
            message_json = json.dumps(message)
            result = await self.redis.publish(channel, message_json)
            logger.debug(f"Published message to channel {channel}: {result} subscribers")
            return result
        except Exception as e:
            logger.error(f"Failed to publish message to channel {channel}: {e}")
            raise
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to Redis channel"""
        if channel not in self._subscribers:
            self._subscribers[channel] = []
        
        # Проверяем, не добавлен ли уже этот callback
        if callback not in self._subscribers[channel]:
            self._subscribers[channel].append(callback)
            logger.info(f"Subscribed to channel {channel}")
        else:
            logger.debug(f"Callback already subscribed to channel {channel}")
        
        # Start listener if not running
        if not self._running:
            logger.info(f"Starting Redis listener for first subscription to channel: {channel}")
            asyncio.create_task(self.start_listening())
        # If listener is already running, subscribe to new channel
        elif self.pubsub:
            logger.info(f"Adding new channel to existing listener: {channel}")
            await self.pubsub.subscribe(channel)
        else:
            logger.info(f"Listener not ready, channel {channel} will be subscribed when listener starts")
    
    async def unsubscribe(self, channel: str, callback: Callable[[Dict[str, Any]], None] = None):
        """Unsubscribe from Redis channel"""
        if channel in self._subscribers:
            if callback:
                if callback in self._subscribers[channel]:
                    self._subscribers[channel].remove(callback)
            else:
                del self._subscribers[channel]
            logger.info(f"Unsubscribed from channel {channel}")
    
    async def start_listening(self):
        """Start listening for messages on subscribed channels"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        self.pubsub = self.redis.pubsub()
        self._running = True
        logger.info(f"Redis listener started, _running={self._running}")
        
        try:
            logger.info(f"Starting Redis pubsub listener on channels: {list(self._subscribers.keys())}")
            
            # Subscribe to all channels
            if self._subscribers:
                await self.pubsub.subscribe(*self._subscribers.keys())
                logger.info(f"Subscribed to channels: {list(self._subscribers.keys())}")
            
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = message["data"]
                    
                    try:
                        message_data = json.loads(data)
                        logger.info(f"Processing message from channel {channel}")
                        await self._handle_message(channel, message_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message from channel {channel}: {e}")
                    except Exception as e:
                        logger.error(f"Error handling message from channel {channel}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in Redis pubsub listener: {e}")
        finally:
            self._running = False
            logger.info("Redis listener stopped")
    
    async def _handle_message(self, channel: str, message_data: Dict[str, Any]):
        """Handle incoming message from Redis channel"""
        if channel in self._subscribers:
            for callback in self._subscribers[channel]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message_data)
                    else:
                        callback(message_data)
                except Exception as e:
                    logger.error(f"Error in callback for channel {channel}: {e}")
    
    async def stop_listening(self):
        """Stop listening for messages"""
        self._running = False
        if self.pubsub:
            await self.pubsub.close()
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self.redis is not None
    
    @property
    def is_listening(self) -> bool:
        """Check if listening for messages"""
        return self._running


class NotificationRedisClient(RedisClient):
    """Specialized Redis client for notification service with pattern subscriptions"""
    
    def __init__(self, host: str = None, port: int = None, db: int = 0):
        super().__init__(host, port, db)
        self.instance_id = os.getenv("INSTANCE_ID", f"instance_{os.getpid()}")
    
    async def publish_notification(self, user_id: int, notification_data: Dict[str, Any]):
        """Publish notification to user-specific channel"""
        channel = f"notification:{user_id}"
        message = {
            "user_id": user_id,
            "instance_id": self.instance_id,
            "timestamp": asyncio.get_event_loop().time(),
            "data": notification_data
        }
        return await self.publish(channel, message)
    
    async def publish_broadcast(self, notification_data: Dict[str, Any]):
        """Publish broadcast notification to all instances"""
        channel = "notifications:broadcast"
        message = {
            "instance_id": self.instance_id,
            "timestamp": asyncio.get_event_loop().time(),
            "data": notification_data
        }
        return await self.publish(channel, message)
    
    async def subscribe_to_user_notifications(self, user_id: int, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to user-specific notifications"""
        channel = f"notification:{user_id}"
        await self.subscribe(channel, callback)
    
    async def subscribe_to_broadcast(self, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to broadcast notifications"""
        channel = "notifications:broadcast"
        await self.subscribe(channel, callback)
    
    async def unsubscribe_from_user_notifications(self, user_id: int, callback: Callable[[Dict[str, Any]], None] = None):
        """Unsubscribe from user-specific notifications"""
        channel = f"notification:{user_id}"
        await self.unsubscribe(channel, callback)
    
    async def unsubscribe_from_broadcast(self, callback: Callable[[Dict[str, Any]], None] = None):
        """Unsubscribe from broadcast notifications"""
        channel = "notifications:broadcast"
        await self.unsubscribe(channel, callback)

    async def subscribe_to_pattern(self, pattern: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to Redis pattern (e.g., notification:*)"""
        if pattern not in self._subscribers:
            self._subscribers[pattern] = []
        
        if callback not in self._subscribers[pattern]:
            self._subscribers[pattern].append(callback)
            logger.info(f"Subscribed to pattern {pattern}")
        
        # Start listener if not running
        if not self._running:
            logger.info(f"Starting Redis listener for pattern subscription: {pattern}")
            asyncio.create_task(self.start_pattern_listening())
        elif self.pubsub:
            logger.info(f"Adding pattern to existing listener: {pattern}")
            await self.pubsub.psubscribe(pattern)
        else:
            logger.info(f"Listener not ready, pattern {pattern} will be subscribed when listener starts")

    async def unsubscribe_from_pattern(self, pattern: str, callback: Callable[[Dict[str, Any]], None] = None):
        """Unsubscribe from Redis pattern"""
        if pattern in self._subscribers:
            if callback:
                if callback in self._subscribers[pattern]:
                    self._subscribers[pattern].remove(callback)
            else:
                del self._subscribers[pattern]
            logger.info(f"Unsubscribed from pattern {pattern}")

    async def start_pattern_listening(self):
        """Start listening for messages on pattern subscriptions"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        self.pubsub = self.redis.pubsub()
        self._running = True
        logger.info(f"Redis pattern listener started, _running={self._running}")
        
        try:
            logger.info(f"Starting Redis pattern listener on patterns: {list(self._subscribers.keys())}")
            
            # Subscribe to all patterns
            if self._subscribers:
                await self.pubsub.psubscribe(*self._subscribers.keys())
                logger.info(f"Subscribed to patterns: {list(self._subscribers.keys())}")
            
            async for message in self.pubsub.listen():
                if message["type"] == "pmessage":
                    pattern = message["pattern"]
                    channel = message["channel"]
                    data = message["data"]
                    
                    try:
                        message_data = json.loads(data)
                        logger.info(f"Processing message from pattern {pattern}, channel {channel}")
                        await self._handle_pattern_message(pattern, channel, message_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode message from pattern {pattern}, channel {channel}: {e}")
                    except Exception as e:
                        logger.error(f"Error handling message from pattern {pattern}, channel {channel}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in Redis pattern listener: {e}")
        finally:
            self._running = False
            logger.info("Redis pattern listener stopped")

    async def _handle_pattern_message(self, pattern: str, channel: str, message_data: Dict[str, Any]):
        """Handle incoming message from Redis pattern"""
        if pattern in self._subscribers:
            for callback in self._subscribers[pattern]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message_data)
                    else:
                        callback(message_data)
                except Exception as e:
                    logger.error(f"Error in callback for pattern {pattern}: {e}")


# Global Redis client instance
redis_client: Optional[NotificationRedisClient] = None


async def get_redis_client() -> NotificationRedisClient:
    """Get global Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = NotificationRedisClient()
        await redis_client.connect()
    return redis_client


async def close_redis_client():
    """Close global Redis client"""
    global redis_client
    if redis_client:
        await redis_client.disconnect()
        redis_client = None 