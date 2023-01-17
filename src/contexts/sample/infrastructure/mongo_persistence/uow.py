from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from contexts.sample.infrastructure.mongo_persistence.repo import MongoSampleRepository
from contexts.sample.infrastructure.cache.cache_repo import CachedRepository
from contexts.sample.infrastructure.mongo_persistence.session import Session
from contexts.shared.cache import CacheProvider
from contexts.shared.uow import IUnitOfWork
from config.settings import settings


class MongoUnitOfWork(IUnitOfWork):
    def __init__(self, cache_provider: CacheProvider) -> None:
        self.cache_provider = cache_provider

    async def __aenter__(self) -> "MongoUnitOfWork":
        client = AsyncIOMotorClient(settings.mongodb_dsm)
        self.session = Session()
        self.samples = MongoSampleRepository(
            client[settings.mongo_dbname], self.session
        )
        if settings.use_cache:
            self.samples = CachedRepository(
                self.samples, self.cache_provider, self.session
            )
        return self

    async def __aexit__(self, *args: Any) -> None:
        await super().__aexit__(*args)

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        pass
