from contexts.sample.core.domain.domain import Sample
from contexts.shared.interfaces import Command
from contexts.shared.uow import IUnitOfWork


class CreateSample(Command):
    attribute: str | None


class CreateSampleHandler:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def run(self, command: CreateSample) -> Sample:
        async with self.uow:
            sample = Sample.new(
                id=self.uow.samples.next_id(),
            )
            await self.uow.samples.asave(sample)
            await self.uow.commit()

        return sample
