from contexts.sample.core.domain.domain import Sample
from contexts.sample.infrastructure.mongo_persistence.uow import MongoUnitOfWork
from composite_root.container import provide


class SampleMother:
    async def a_sample(
        self,
        reference: str | None = None,
    ) -> Sample:
        async with provide(MongoUnitOfWork) as uow:
            sample = Sample.new(
                id=uow.samples.next_id(),
            )

            if reference:
                sample.reference = reference

            await uow.samples.asave(sample)
            await uow.commit()
        return sample
