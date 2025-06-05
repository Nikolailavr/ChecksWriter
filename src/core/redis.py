import asyncio
import redis.asyncio as redis

class HybridRedisClient:
    def __init__(self, async_client):
        self.async_client = async_client

    def __getattr__(self, name):
        async_method = getattr(self.async_client, name)

        def sync_method(*args, **kwargs):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # sync context — запускаем event loop и ждём
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(async_method(*args, **kwargs))
                loop.close()
                return result
            else:
                # async context — возвращаем coroutine
                return async_method(*args, **kwargs)

        return sync_method


# Redis
async_redis_client = redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    decode_responses=True,  # чтобы не приходилось вручную декодировать строки
)

redis_client = HybridRedisClient(async_redis_client)
