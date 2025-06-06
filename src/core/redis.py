import redis.asyncio as async_redis
import redis


from core import settings

# Redis
async_redis_client = async_redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    decode_responses=True,  # чтобы не приходилось вручную декодировать строки
)

<<<<<<< HEAD
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
=======
redis_client = redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    decode_responses=True,
)
>>>>>>> d14dec3dbf8c40728b153227d7f6205b5442f9c7
