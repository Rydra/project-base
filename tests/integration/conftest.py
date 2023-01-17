import pytest
from aiocache import caches

from contexts.shared.anyio import async_to_sync


@pytest.fixture(autouse=True)
def bootstrap_cache():
    from contexts.shared.cache import init_cache

    init_cache()
    yield

    async def _():
        try:
            await caches.get("redis_alt").clear(namespace="samples")
        except TypeError:
            # This error happens only if the cache is empty. This could have
            # been handled better in the library...
            pass

    async_to_sync(_)
