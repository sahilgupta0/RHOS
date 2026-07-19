"""
RHOS Base Repository.

Generic async MongoDB repository with CRUD operations.
"""

from __future__ import annotations

import logging
import re
from typing import Any, TypeVar

from app.core.mongodb import get_mongodb_db

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _parse_filters(filters: list[tuple[str, str, Any]] | None) -> dict[str, Any]:
    """Parse Firestore-style filters into MongoDB query filter dictionary."""
    query = {}
    if not filters:
        return query

    op_map = {
        "==": "$eq",
        "!=": "$ne",
        ">=": "$gte",
        "<=": "$lte",
        ">": "$gt",
        "<": "$lt",
        "array-contains": "$eq",  # In MongoDB, if field is an array, {field: value} matches if value is in array
    }

    field_conditions = {}
    for field, op, value in filters:
        if field == "id":
            field = "_id"
        mongo_op = op_map.get(op, "$eq")
        if mongo_op == "$eq":
            field_conditions[field] = value
        else:
            if field not in field_conditions or not isinstance(
                field_conditions[field], dict
            ):
                field_conditions[field] = {}
            field_conditions[field][mongo_op] = value

    for field, cond in field_conditions.items():
        query[field] = cond
    return query


class BaseRepository:
    """Generic MongoDB repository with common CRUD operations."""

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @property
    def _collection(self):
        """Get the MongoDB collection reference."""
        db = get_mongodb_db()
        if db is None:
            raise ConnectionError(
                "MongoDB is not initialized. Check MongoDB configuration."
            )
        return db[self.collection_name]

    async def get_by_id(self, doc_id: str) -> dict[str, Any] | None:
        """Get a document by ID."""
        try:
            doc = await self._collection.find_one({"_id": doc_id})
            if doc:
                doc["id"] = str(doc.pop("_id"))
                return doc
            return None
        except Exception as e:
            logger.error(
                "Error getting document %s/%s: %s", self.collection_name, doc_id, e
            )
            raise

    async def create(self, data: dict[str, Any], doc_id: str | None = None) -> str:
        """Create a new document. Returns the document ID."""
        try:
            doc_data = data.copy()
            if doc_id:
                doc_data["_id"] = doc_id
            else:
                import uuid

                doc_id = uuid.uuid4().hex
                doc_data["_id"] = doc_id

            await self._collection.insert_one(doc_data)
            return doc_id
        except Exception as e:
            logger.error("Error creating document in %s: %s", self.collection_name, e)
            raise

    async def update(self, doc_id: str, data: dict[str, Any]) -> None:
        """Update an existing document."""
        try:
            await self._collection.update_one({"_id": doc_id}, {"$set": data})
        except Exception as e:
            logger.error(
                "Error updating document %s/%s: %s", self.collection_name, doc_id, e
            )
            raise

    async def delete(self, doc_id: str) -> None:
        """Delete a document."""
        try:
            await self._collection.delete_one({"_id": doc_id})
        except Exception as e:
            logger.error(
                "Error deleting document %s/%s: %s", self.collection_name, doc_id, e
            )
            raise

    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str | None = None,
        direction: str = "ASCENDING",
        filters: list[tuple[str, str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """
        List documents with optional filtering, ordering, and pagination.

        Args:
            limit: Maximum number of documents to return.
            offset: Number of documents to skip.
            order_by: Field to order by.
            direction: Sort direction ('ASCENDING' or 'DESCENDING').
            filters: List of (field, operator, value) tuples for filtering.
        """
        try:
            query = _parse_filters(filters)
            cursor = self._collection.find(query)

            # Apply ordering
            if order_by:
                sort_field = "_id" if order_by == "id" else order_by
                from pymongo import ASCENDING, DESCENDING

                sort_dir = (
                    DESCENDING if direction.upper() == "DESCENDING" else ASCENDING
                )
                cursor = cursor.sort(sort_field, sort_dir)

            # Apply pagination
            if offset > 0:
                cursor = cursor.skip(offset)
            cursor = cursor.limit(limit)

            results = []
            async for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                results.append(doc)

            return results
        except Exception as e:
            logger.error("Error listing documents in %s: %s", self.collection_name, e)
            raise

    async def count(self, filters: list[tuple[str, str, Any]] | None = None) -> int:
        """Count documents matching optional filters."""
        try:
            query = _parse_filters(filters)
            return await self._collection.count_documents(query)
        except Exception as e:
            logger.error("Error counting documents in %s: %s", self.collection_name, e)
            return 0

    async def search(
        self, field: str, value: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Simple search by field value (exact match or prefix)."""
        try:
            query = {field: {"$regex": f"^{re.escape(value)}", "$options": "i"}}
            cursor = self._collection.find(query).limit(limit)
            results = []
            async for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                results.append(doc)
            return results
        except Exception as e:
            logger.error(
                "Error searching %s by %s=%s: %s", self.collection_name, field, value, e
            )
            return []
