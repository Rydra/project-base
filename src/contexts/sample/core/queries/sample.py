from contexts.shared.anyio import ResultGatheringTaskgroup
from contexts.shared.interfaces import Query
from contexts.sample.core.domain.domain import Sample, ListResult
from contexts.shared.typing import Id
from contexts.shared.uow import IUnitOfWork


class ListSamples(Query):
    pass


class ListSamplesHandler:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def run(self, command: ListSamples) -> ListResult[Sample]:
        async with self.uow:
            async with ResultGatheringTaskgroup() as tg:
                samples = tg.start_soon(self.uow.samples.aall)
                count = tg.start_soon(self.uow.samples.count)

        return ListResult(count=tg.get_result(count), results=tg.get_result(samples))


class GetSample(Query):
    id: Id


class GetSampleHandler:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    async def run(self, command: GetSample) -> Sample:
        async with self.uow:
            sample = await self.uow.samples.aget(command.id)
            return sample
