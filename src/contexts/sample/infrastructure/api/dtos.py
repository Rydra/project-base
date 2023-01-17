from pydantic import BaseModel

from contexts.sample.core.domain.domain import Sample
from contexts.shared.typing import Id


class SampleDto(BaseModel):
    id: Id
    reference: str

    @staticmethod
    def from_domain(sample: Sample) -> "SampleDto":
        return SampleDto(
            id=sample.id,
            reference=sample.reference,
        )


class ListSamplesResponse(BaseModel):
    results: list[SampleDto]
