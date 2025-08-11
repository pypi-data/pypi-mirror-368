import typing as tp
from functools import lru_cache

import typing_extensions as tpe
from openai import AsyncOpenAI

from ._base import Base
from .blobs import Blobs
from .collections import Collections
from .objects import Objects
from .query import Query
from .vector import Vectors

__all__ = [
    "Collections",
    "Objects",
    "Vectors",
    "Query",
    "Blobs",
    "Quipubase",
    "QuipuModel",
]


class Quipubase(AsyncOpenAI):
    """Quipubase client"""

    def __init__(
        self,
        *,
        base_url: str = "https://quipubase.oscarbahamonde.com/v1",
        api_key: str = "[DEFAULT]",
        timeout: int = 86400,
    ):
        super().__init__(base_url=base_url, api_key=api_key, timeout=timeout)

    @property
    def collections(self):
        """
        Collections endpoint of Quipubase
        """
        return Collections(client=self._client)

    @property
    def objects(self):
        """
        Objects endpoint of Quipubase
        """
        return Objects(client=self._client)

    @property
    def query(self):
        """
        Live Query Resource
        """
        return Query(client=self._client)

    @property
    def vector(self):
        """
        Vector Resource
        """
        return Vectors(client=self._client)

    @property
    def blobs(self):
        """
        Blobs
        """
        return Blobs(client=self._client)


class QuipuModel(Base):
    """Base model for Quipubase"""

    @classmethod
    @lru_cache
    def get_client(
        cls,
        *,
        base_url: str = "https://quipubase.oscarbahamonde.com/v1",
        api_key: str = "[DEFAULT]",
        timeout: int = 86400,
    ):
        """Get a client instance"""
        return Quipubase(base_url=base_url, api_key=api_key, timeout=timeout)

    @classmethod
    @lru_cache
    async def _get_collection_id(cls):
        """Upsert the model"""
        client = cls.get_client()
        schema = cls.model_json_schema()
        collection = await client.collections.create(json_schema=schema)
        return collection.id

    @classmethod
    async def subscribe(cls, *, collection_id: str):
        """Listen to a collection"""
        client = cls.get_client()
        async for event in client.objects.sub(collection_id=collection_id):
            if isinstance(event.data, dict):
                yield cls.model_validate(event.data)
            else:
                for item in event.data:
                    yield cls.model_validate(item)

    @classmethod
    async def delete(cls, *, id: str):
        """Delete a model"""
        client = cls.get_client()
        collection_id = await cls._get_collection_id()
        return await client.objects.pub(
            collection_id=collection_id, event="delete", id=id
        )

    @classmethod
    async def query(cls, *, collection_id: str, **kwargs: tp.Any) -> list[tpe.Self]:
        """Query a collection"""
        client = cls.get_client()
        response = await client.objects.pub(
            collection_id=collection_id, event="query", data=kwargs
        )
        if isinstance(response.data, dict):
            return [cls.model_validate(response.data)]
        return [cls.model_validate(item) for item in response.data]

    async def upsert(self):
        """Upsert a model"""
        client = self.get_client()
        collection_id = await self._get_collection_id()
        object_id = self.model_dump().get("id")
        if isinstance(object_id, str):
            return await client.objects.pub(
                collection_id=collection_id,
                event="update",
                id=object_id,
                data=self.model_dump(),
            )
        return await client.objects.pub(
            collection_id=collection_id, event="create", data=self.model_dump()
        )
