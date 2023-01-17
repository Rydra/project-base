from abc import ABC, abstractmethod

from contexts.sample.core.domain.domain import Sample
from contexts.shared.typing import Id


class ISampleRepository(ABC):
    @abstractmethod
    def next_id(self) -> Id:
        ...

    @abstractmethod
    async def aall(self) -> list[Sample]:
        ...

    @abstractmethod
    async def count(self) -> int:
        ...

    @abstractmethod
    async def asave(self, sample: Sample) -> None:
        ...

    @abstractmethod
    async def aget(self, id: int) -> Sample:
        ...
