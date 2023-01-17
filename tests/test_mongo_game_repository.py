from hamcrest import *

from contexts.sample.core.domain.domain import Sample
from contexts.sample.infrastructure.mongo_persistence.uow import MongoUnitOfWork
from composite_root.container import provide


class TestMongoSampleRepository:
    async def test_save_new_sample_with_uow(self, anyio_backend):
        uow = provide(MongoUnitOfWork)
        async with uow:
            sample = Sample.new(id=uow.samples.next_id())
            await uow.samples.asave(sample)
            await uow.commit()

            sample_from_db = await uow.samples.aget(sample.id)
            assert_that(
                sample_from_db,
                has_properties(
                    reference=is_(str),
                ),
            )

    async def test_save_update_sample_with_uow(self, anyio_backend):
        uow = provide(MongoUnitOfWork)
        async with uow:
            new_sample = Sample.new(id=uow.samples.next_id())
            await uow.samples.asave(new_sample)
            await uow.commit()

        async with uow:
            sample = await uow.samples.aget(new_sample.id)
            await uow.samples.asave(sample)
            await uow.commit()

            sample_from_db = await uow.samples.aget(sample.id)
            assert_that(
                sample_from_db,
                has_properties(
                    id=new_sample.id,
                    reference=is_(str),
                ),
            )
