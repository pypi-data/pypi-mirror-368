import os
import redis.asyncio as redis
import logging


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
logger = logging.getLogger(__name__)

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def init_redis():
    try:
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")