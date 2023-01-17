from typing import Callable

from aiocache import caches
from aiocache.base import BaseCache

from contexts.sample.infrastructure.mongo_persistence.uow import MongoUnitOfWork
import pinject

from contexts.shared.cache import CacheProvider
from config.settings import settings


class SampleBindingSpec(pinject.BindingSpec):
    def configure(self, bind: Callable) -> None:
        bind("uow", to_class=MongoUnitOfWork)

    def provide_cache(self) -> BaseCache:
        if settings.test_run:
            return caches.get("default")

        return caches.get("redis_alt")

    def provide_cache_provider(self, cache: BaseCache) -> CacheProvider:
        return CacheProvider(cache)
