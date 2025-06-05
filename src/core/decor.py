import asyncio
import functools


def hybrid_async(func):
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            # Проверяем, есть ли запущенный event loop (async context)
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Если нет — значит sync контекст, создаём новый loop и запускаем
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(func(*args, **kwargs))
            loop.close()
            return result
        else:
            # Если loop уже есть — вызываем асинхронно
            return func(*args, **kwargs)

    # Возвращаем функцию, которая в async контексте возвращает coroutine, в sync — результат
    return sync_wrapper
