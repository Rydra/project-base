import logging

from bson import ObjectId
from bson.errors import InvalidId
from motor.core import AgnosticDatabase
from pymongo import InsertOne, UpdateOne

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
        self.seen: set[Id] = set()

    async def aall(self) -> list[Sample]:
        items = [self._to_domain(d) async for d in self.sample_collection.find()]
        self.seen.union(set(i.id for i in items))
        return items

    def next_id(self) -> Id:
        return str(ObjectId())

    async def asave(self, sample: Sample) -> None:
        sample_dict = {"reference": sample.reference, "version": sample.version + 1}

        if not sample.id:
            self.session.add_operation(self.sample_collection, InsertOne(sample_dict))
        else:
            if sample.id in self.seen:
                self.session.add_operation(
                    self.sample_collection,
                    UpdateOne(
                        {"_id": ObjectId(sample.id), "version": sample.version},
                        {"$set": sample_dict},
                    ),
                )
            else:
                self.session.add_operation(
                    self.sample_collection,
                    InsertOne({"_id": ObjectId(sample.id), **sample_dict}),
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

        item = self._to_domain(document)
        self.seen.add(id)
        return item

    def _to_domain(self, document: dict) -> Sample:
        return Sample(
            id=str(document["_id"]),
            reference=document["reference"],
            version=document["version"],
        )
