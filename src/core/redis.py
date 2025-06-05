import redis.asyncio as redis

from core import settings

# Redis
redis_client = redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    decode_responses=True,  # чтобы не приходилось вручную декодировать строки
)

