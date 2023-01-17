from contexts.sample.core.domain.domain import Sample
from contexts.sample.core.domain.interfaces import ISampleRepository
from contexts.sample.infrastructure.mongo_persistence.session import Session
from contexts.shared.cache import CacheProvider
from contexts.shared.typing import Id


class CachedRepository(ISampleRepository):
    """
    The cache stampede uses the proper caching strategy of lazy reads.
    """

    namespace = "samples"

    def __init__(
        self, repository: ISampleRepository, cache: CacheProvider, session: Session
    ) -> None:
        self.repository = repository
        self.cache = cache
        self.session = session

    async def aall(self) -> list[Sample]:
        return await self.cache.get_or_update(
            "aall",
            namespace=self.namespace,
            f=self.repository.aall,
        )

    def next_id(self) -> Id:
        return self.repository.next_id()

    async def aget(self, id: Id) -> Sample:
        return await self.cache.get_or_update(
            f"aget-{id}", namespace=self.namespace, f=self.repository.aget, args=(id,)
        )

    async def asave(self, sample: Sample) -> None:
        # Beware: save operations from a repository, if they are under
        # a unit of work session, will not do any physical save. When we save
        await self.repository.asave(sample)
        self.session.add_postcommit_hook(
            lambda: self.cache.delete("aall", namespace=self.namespace)
        )
        self.session.add_postcommit_hook(
            lambda: self.cache.delete(f"aget-{sample.id}", namespace=self.namespace)
        )
        self.session.add_postcommit_hook(
            lambda: self.cache.delete(f"count", namespace=self.namespace)
        )

    async def count(self) -> int:
        return await self.cache.get_or_update(
            "count", namespace=self.namespace, f=self.repository.count
        )
