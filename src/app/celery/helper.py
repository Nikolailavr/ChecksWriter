import asyncio
from typing import Coroutine, Callable, Any


class CeleryHelper:

    def __init__(self):
        self._loop = asyncio.new_event_loop()

    def run(
        self,
        coro: Coroutine | Callable[..., Coroutine],
        *args,
        **kwargs,
    ) -> Any:
        return self._loop.run_until_complete(coro(*args, **kwargs))
