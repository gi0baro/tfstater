import asyncio

from functools import partial


class StateLockedException(Exception):
    ...


async def run_in_loop(f, args=[], kwargs={}, timeout=5):
    if args or kwargs:
        f = partial(f, *args, **kwargs)
    return await asyncio.wait_for(
        asyncio.get_event_loop().run_in_executor(None, f), timeout
    )
