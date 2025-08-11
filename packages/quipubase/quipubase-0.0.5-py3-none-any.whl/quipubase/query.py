# quipubase/query.py
#
# Asynchronous client for Quipubase query endpoints.

from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from httpx import AsyncClient
from loguru import logger

from ._base import Base

# --- Query API Request Models ---


class LiveQueryDatasetMetadata(tpe.TypedDict):
    """Metadata for a live query dataset."""

    key: str
    bucket: tpe.NotRequired[str]
    namespace: tpe.NotRequired[str]


class LiveQueryDatasetQuery(LiveQueryDatasetMetadata):
    """Request model for querying a live dataset."""

    query: str


class LiveQueryDatasetUpdate(LiveQueryDatasetMetadata):
    """Request model for updating a live dataset."""

    data: tp.List[tp.Dict[str, tp.Any]]


class Adapter(tpe.TypedDict):
    """Request model for creating a file-based dataset."""

    engine: tp.Literal["file", "mongodb", "postgresql"]
    uri: str
    query: str
    key: tpe.NotRequired[str]
    namespace: tpe.NotRequired[str]
    bucket: tpe.NotRequired[str]


# --- Query API Response Models ---


class DatasetMetadataResponse(Base):
    """Response model for dataset metadata."""

    key: str
    bucket: str
    namespace: str


class QueryLiveResponse(Base):
    """Response model for live query operations (PUT, PATCH)."""

    data: tp.List[tp.Dict[str, tp.Any]]
    json_schema: tp.Dict[str, tp.Any]
    key: str


class DeleteQueryDatasetResponse(Base):
    """Response model for deleting a live query dataset."""

    success: bool


class JsonSchemaModel(tpe.TypedDict):
    """Response model for getting a dataset's JSON schema."""

    ...


class Query(tp.NamedTuple):
    """Asynchronous client for Quipubase query endpoints."""

    client: AsyncClient

    async def list(
        self,
        namespace: str = "default",
        bucket: str = "quipu-store",
    ) -> tp.List[DatasetMetadataResponse]:
        """
        Get a list of datasets.

        Args:
            namespace: The namespace to filter datasets by.
            bucket: The bucket to filter datasets by.

        Returns:
            A list of DatasetMetadataResponse objects.
        """
        params = {"namespace": namespace, "bucket": bucket}
        response = await self.client.get("/query/live", params=params)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return [DatasetMetadataResponse(**d) for d in data]

    async def create(self, **kwargs: tpe.Unpack[Adapter]) -> QueryLiveResponse:
        """
        Create a new live query dataset.

        Args:
            **kwargs: Keyword arguments for the request object.

        Returns:
            A QueryLiveResponse object.
        """
        response = await self.client.post("/query/live", json=kwargs)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryLiveResponse(**data)

    async def retrieve(
        self, **kwargs: tpe.Unpack[LiveQueryDatasetQuery]
    ) -> QueryLiveResponse:
        """
        Get the data of a specific dataset.

        Args:
            **kwargs: Keyword arguments for the request object.

        Returns:
            A QueryLiveResponse object.
        """
        response = await self.client.put("/query/live", json=kwargs)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryLiveResponse(**data)

    async def update(
        self, **kwargs: tpe.Unpack[LiveQueryDatasetUpdate]
    ) -> QueryLiveResponse:
        """
        Update the data of a specific dataset.

        Args:
            **kwargs: Keyword arguments for the request object.

        Returns:
            A QueryLiveResponse object.
        """
        response = await self.client.patch("/query/live", json=kwargs)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryLiveResponse(**data)

    async def delete(
        self,
        key: str,
        bucket: str = "quipu-store",
        namespace: str = "default",
    ) -> DeleteQueryDatasetResponse:
        """
        Delete a live query dataset.

        Args:
            key: The key of the dataset to delete.
            bucket: The bucket of the dataset to delete.
            namespace: The namespace of the dataset to delete.

        Returns:
            A DeleteQueryDatasetResponse object indicating success.
        """
        response = await self.client.delete(
            "/query/live",
            params={"key": key, "bucket": bucket, "namespace": namespace},
        )
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return DeleteQueryDatasetResponse(**data)

    async def describe(
        self, **kwargs: tpe.Unpack[LiveQueryDatasetMetadata]
    ) -> JsonSchemaModel:
        """
        Get the JSON schema of a dataset.

        Args:
            **kwargs: Keyword arguments for the request object.

        Returns:
            A JsonSchemaModel object containing the dataset's schema.
        """
        response = await self.client.post("/query/schema", json=kwargs)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return JsonSchemaModel(**data)
