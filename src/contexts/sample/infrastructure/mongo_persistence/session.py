from collections import defaultdict
from typing import Any

from motor.core import AgnosticCollection
from pymongo import UpdateOne

from contexts.shared.exceptions import ConcurrencyError
from contexts.shared.uow import BaseSession


class Session(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.operations: dict = defaultdict(list)

    def add_operation(self, collection: AgnosticCollection, operation: Any) -> None:
        self.operations[collection].append(operation)

    async def _commit(self) -> None:
        for collection, operations in self.operations.items():
            result = await collection.bulk_write(operations)
            # Count the number of modifications. If this number differs from the requested number of updates
            # we have a concurrency error in front of us
            num_updates = sum(1 for op in operations if isinstance(op, UpdateOne))
            if result.modified_count != num_updates:
                raise ConcurrencyError(
                    f"Concurrency error upon writing into the collection {collection.name}"
                )
