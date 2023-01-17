import pytest
from aiocache import caches
from django.test import RequestFactory

from contexts.shared.anyio import async_to_sync
from contexts.shared.cache import init_cache


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def bootstrap_cache():
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
