import redis.asyncio as async_redis
import redis


from core import settings

# Redis
async_redis_client = async_redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    password=settings.redis.PASSWORD,
    db=settings.redis.DB,
    decode_responses=True,  # чтобы не приходилось вручную декодировать строки
)

redis_client = redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    password=settings.redis.PASSWORD,
    db=settings.redis.DB,
    decode_responses=True,
)
