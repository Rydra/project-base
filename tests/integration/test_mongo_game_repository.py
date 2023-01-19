from hamcrest import *

from contexts.sample.core.domain.domain import Sample
from contexts.sample.infrastructure.mongo_persistence.uow import MongoUnitOfWork
from composite_root.container import provide
from contexts.shared.exceptions import ConcurrencyError


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

    async def test_optimistic_concurrency_is_in_place(self, anyio_backend):
        uow = provide(MongoUnitOfWork)
        async with uow:
            new_sample = Sample.new(id=uow.samples.next_id())
            await uow.samples.asave(new_sample)
            await uow.commit()

        async with uow:
            sample_copy1 = await uow.samples.aget(new_sample.id)
            sample_copy2 = await uow.samples.aget(new_sample.id)

            await uow.samples.asave(sample_copy1)
            await uow.samples.asave(sample_copy2)

            captured_exception = None
            try:
                await uow.commit()
            except Exception as e:
                captured_exception = e

        assert_that(captured_exception, is_(ConcurrencyError))
