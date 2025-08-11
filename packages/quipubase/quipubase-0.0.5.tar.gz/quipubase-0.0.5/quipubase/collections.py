from __future__ import annotations

import typing as tp

from httpx import AsyncClient
from loguru import logger

from ._base import Base


class CollectionModel(Base):
    """Response model for a collection."""

    id: str
    sha: str
    json_schema: str | dict[str, tp.Any]
    created_at: str
    updated_at: str


class CollectionDeleteModel(Base):
    """Response model for deleting a collection."""

    code: int


class Collections(tp.NamedTuple):
    """Asynchronous client for Quipubase collection endpoints."""

    client: AsyncClient

    async def create(self, *, json_schema: dict[str, tp.Any]) -> CollectionModel:
        """
        Create a new collection.

        Args:
            json_schema: The JSON schema for the collection.

        Returns:
            A CollectionModel object.
        """
        response = await self.client.post("/collections", json=json_schema)
        data = response.json()
        logger.info(data)
        return CollectionModel(**data)

    async def retrieve(self, *, collection_id: str) -> CollectionModel:
        """
        Retrieve a collection by ID.

        Args:
            collection_id: The ID of the collection to retrieve.

        Returns:
            A CollectionModel object.
        """
        response = await self.client.get(f"/collections/{collection_id}")
        data = response.json()
        logger.info(data)
        return CollectionModel(**data)

    async def delete(self, *, collection_id: str) -> CollectionDeleteModel:
        """
        Delete a collection by ID.

        Args:
            collection_id: The ID of the collection to delete.

        Returns:
            A CollectionDeleteModel object.
        """
        response = await self.client.delete(f"/collections/{collection_id}")
        data = response.json()
        logger.info(data)
        return CollectionDeleteModel(**data)

    async def list(self) -> tp.List[CollectionModel]:
        """
        List all collections.

        Returns:
            A list of CollectionModel objects.
        """
        response = await self.client.get("/collections")
        data = response.json()
        logger.info(data)
        return [CollectionModel(**item) for item in data]
