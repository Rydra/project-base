from typing import cast, Generic

import strawberry

from contexts.auth.infrastructure.graphql.context import IsAuthenticated
from contexts.sample.core.queries.sample import (
    ListSamplesHandler,
    ListSamples,
    GetSampleHandler,
    GetSample,
)
from contexts.shared.exceptions import NotFound
from contexts.shared.typing import T
from composite_root.container import provide

from contexts.sample.core.domain.domain import Sample


@strawberry.type
class Page(Generic[T]):  # type: ignore
    count: int
    results: list[T]


@strawberry.type
class SampleNode:
    id: str
    reference: str

    @staticmethod
    def from_domain(sample: Sample) -> "SampleNode":
        return SampleNode(id=sample.id, reference=sample.reference)


@strawberry.type
class SampleQueries:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def samples(self) -> Page[SampleNode]:  # type: ignore
        samples = await provide(ListSamplesHandler).run(ListSamples())
        return Page(count=samples.count, results=samples.results)

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def sample(self, id: str) -> SampleNode | None:
        try:
            sample = await provide(GetSampleHandler).run(GetSample(id=id))
            return cast(SampleNode, sample)
        except NotFound:
            return None
