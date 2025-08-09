import asyncio, random


async def with_retries(coro, max_retries=5, base_delay=1.0):
    for i in range(max_retries):
        try:
            return await coro()
        except Exception as e:
            if getattr(e, 'status', None) == 429:
                await asyncio.sleep(
                    base_delay * (2 ** i) + random.uniform(0, 0.5),
                );
                continue
            raise
    raise RuntimeError('Max retries exceeded')
