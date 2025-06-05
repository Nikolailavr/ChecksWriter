import asyncio
import redis.asyncio as redis

from core import settings

class HybridRedisClient:
    def __init__(self, async_client):
        self.async_client = async_client

    def __getattr__(self, name):
        attr = getattr(self.async_client, name)

        if inspect.iscoroutinefunction(attr):
            def sync_method(*args, **kwargs):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(attr(*args, **kwargs))
                    loop.close()
                    return result
                else:
                    return attr(*args, **kwargs)

            return sync_method

        # На случай, если attr сам coroutine, а не coroutine function
        elif inspect.iscoroutine(attr):
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(attr)
                loop.close()
                return result
            else:
                return attr

        else:
            return attr


# Redis
async_redis_client = redis.Redis(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    decode_responses=True,  # чтобы не приходилось вручную декодировать строки
)

redis_client = HybridRedisClient(async_redis_client)
