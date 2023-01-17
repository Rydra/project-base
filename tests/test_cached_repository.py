from collections import defaultdict
from typing import Any

import pytest
from aiocache import caches
from hamcrest import *

from contexts.sample.core.domain.domain import Sample
from contexts.sample.core.domain.interfaces import ISampleRepository
from contexts.sample.infrastructure.cache.cache_repo import CachedRepository
from contexts.sample.infrastructure.mongo_persistence.session import Session
from contexts.shared.anyio import async_to_sync
from contexts.shared.cache import CacheProvider
from contexts.shared.typing import Id


def awaitable(value: Any) -> Any:
    async def _(*args, **kwargs):
        return value

    return _


class SampleRepositoryStub(ISampleRepository):
    def __init__(self):
        self.call_counts = defaultdict(int)

    def next_id(self) -> Id:
        ...

    async def aall(self) -> list[Sample]:
        self.call_counts["aall"] += 1
        return [Sample.new()]

    async def count(self) -> int:
        ...

    async def asave(self, sample: Sample) -> None:
        ...

    async def aget(self, id: int) -> Sample:
        self.call_counts["aget"] += 1
        return Sample.new()


@pytest.mark.integrationtest
class TestCachedRepository:
    async def test_cache_all(self, anyio_backend, request):
        def clear_cache():
            async def _():
                return await caches.get("redis_alt").clear(namespace="samples")

            async_to_sync(_)

        request.addfinalizer(clear_cache)
        sample_repository_stub = SampleRepositoryStub()
        cached_repository = CachedRepository(
            sample_repository_stub, CacheProvider(caches.get("redis_alt")), Session()
        )

        await cached_repository.aall()
        await cached_repository.aall()

        assert_that(sample_repository_stub.call_counts["aall"], is_(1))

    async def test_saving_clears_the_cache_for_listing(self, anyio_backend, request):
        def clear_cache():
            async def _():
                return await caches.get("redis_alt").clear(namespace="samples")

            async_to_sync(_)

        request.addfinalizer(clear_cache)
        sample_repository_stub = SampleRepositoryStub()
        session = Session()
        cached_repository = CachedRepository(
            sample_repository_stub, CacheProvider(caches.get("redis_alt")), session
        )

        await cached_repository.aall()
        await cached_repository.asave(Sample.new(id="AAA"))
        await session.commit()

        await cached_repository.aall()

        assert_that(sample_repository_stub.call_counts["aall"], is_(2))

    async def test_saving_clears_the_cache_for_individual_get(
        self, anyio_backend, request
    ):
        def clear_cache():
            async def _():
                return await caches.get("redis_alt").clear(namespace="samples")

            async_to_sync(_)

        request.addfinalizer(clear_cache)
        sample_repository_stub = SampleRepositoryStub()

        session = Session()
        cached_repository = CachedRepository(
            sample_repository_stub, CacheProvider(caches.get("redis_alt")), session
        )

        await cached_repository.aget("AAA")
        await cached_repository.asave(Sample.new(id="AAA"))

        await session.commit()
        await cached_repository.aget("AAA")
        await cached_repository.aget("AAA")

        assert_that(sample_repository_stub.call_counts["aget"], is_(2))
