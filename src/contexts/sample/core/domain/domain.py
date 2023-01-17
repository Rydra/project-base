import uuid
from dataclasses import dataclass
from typing import Generic

from contexts.shared.typing import Id, T


@dataclass
class ListResult(Generic[T]):  # type: ignore
    count: int
    results: list[T]


def create_reference() -> str:
    """Generate a default stream name.

    The stream name will be completely random, based on the UUID generator
    passed onto hex format and cutr down to 8 characters. Remeber, UUID4's
    are 32 characters in length, so we cut it
    """
    divider = 3  # Divided by 3 generates 8 characters, by 2, 16 characters
    random_uuid = uuid.uuid4()
    stream_name = random_uuid.hex[: int(len(random_uuid.hex) / divider)]
    return stream_name


class Sample:
    def __init__(
        self,
        id: Id | None,
        reference: str,
    ):
        self.id = id
        self.reference = reference

    @staticmethod
    def new(id: Id | None = None) -> "Sample":
        reference = create_reference().upper()
        return Sample(
            id,
            reference,
        )
