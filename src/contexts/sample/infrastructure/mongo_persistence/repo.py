import logging

from bson import ObjectId
from bson.errors import InvalidId
from motor.core import AgnosticDatabase
from pymongo import InsertOne, ReplaceOne

from contexts.sample.core.domain.domain import Sample
from contexts.sample.core.domain.interfaces import ISampleRepository
from contexts.sample.infrastructure.mongo_persistence.session import Session
from contexts.shared.exceptions import NotFound
from contexts.shared.typing import Id

logger = logging.getLogger()


class MongoSampleRepository(ISampleRepository):
    def __init__(self, database: AgnosticDatabase, session: Session) -> None:
        self.session = session
        self.sample_collection = database.sample_collection

    async def aall(self) -> list[Sample]:
        return [self._to_domain(d) async for d in self.sample_collection.find()]

    def next_id(self) -> Id:
        return str(ObjectId())

    async def asave(self, sample: Sample) -> None:
        sample_dict = {
            "reference": sample.reference,
        }

        if not sample.id:
            self.session.add_operation(self.sample_collection, InsertOne(sample_dict))
        else:
            self.session.add_operation(
                self.sample_collection,
                ReplaceOne({"_id": ObjectId(sample.id)}, sample_dict, upsert=True),
            )

    async def count(self) -> int:
        return await self.sample_collection.count_documents({})

    async def aget(self, id: Id) -> Sample:
        try:
            document = await self.sample_collection.find_one({"_id": ObjectId(id)})
        except InvalidId:
            document = None

        if not document:
            raise NotFound()

        return self._to_domain(document)

    def _to_domain(self, document: dict) -> Sample:
        return Sample(
            id=str(document["_id"]),
            reference=document["reference"],
        )
