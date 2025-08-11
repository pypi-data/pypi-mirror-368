from __future__ import annotations

import typing as tp

import typing_extensions as tpe
from httpx import AsyncClient
from loguru import logger
from pydantic import BaseModel as Base
from pydantic import Field
from rustid import uuid4

from ._base import Base

MetaDataValue: tpe.TypeAlias = tp.Union[
    str,
    int,
    float,
    bool,
    list[str],
    list[int],
    list[float],
    list[bool],
    dict[str, str | int | float | bool | list[str] | list[int] | list[float]],
    list[
        dict[
            str,
            str | int | float | bool | list[str] | list[int] | list[float] | list[bool],
        ]
    ],
]


class EmbedText(tpe.TypedDict):
    """Model for upserting texts into the vector store."""

    input: tp.List[str] | str
    model: tpe.Literal["gemini-embedding-001"]
    metadata: list[dict[str, MetaDataValue]] | dict[str, MetaDataValue]

class QueryText(tpe.TypedDict):
    """Model for querying the vector store."""

    input: str
    top_k: int
    model: tpe.Literal["gemini-embedding-001"]


class UpsertItem(tpe.TypedDict):
    """Model for a single upsert item."""

    id: str
    metadata: tp.Dict[str, MetaDataValue]


class Embedding(Base):
    """
    Represents a text embedding with associated metadata.

    Attributes:
        id (str): Unique identifier for the embedding (auto-generated UUID)
        content (str | list[str]): Text content or list of strings
        embedding (NDArray[np.float32]): Vector representation of the content
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the embedding (auto-generated UUID)",
    )
    score: float
    metadata: dict[str, MetaDataValue]

class QueryItem(UpsertItem):
    """Model for a single query item."""
    id: str
    score: float
    metadata: dict[str, MetaDataValue]

class UpsertResponse(Base):
    """Model for the response after an upsert operation."""

    count: int = Field(..., description="The number of embeddings that were upserted.")
    ellapsed: float = Field(
        ..., description="The time taken for the upsert in seconds."
    )
    data: tp.List[UpsertItem] = Field(..., description="List of upserted embeddings.")


class QueryResponse(Base):
    """Model for the response from a query operation."""

    data: tp.List[QueryItem] = Field(
        ..., description="List of matched texts and their similarity scores."
    )
    count: int = Field(..., description="The total number of matches found.")
    ellapsed: float = Field(..., description="The time taken for the query in seconds.")


class DeleteResponse(Base):
    """Model for the response after a delete operation."""

    data: tp.List[str] = Field(..., description="List of deleted IDs.")
    count: int = Field(..., description="The number of embeddings that were deleted.")
    ellapsed: float = Field(
        ..., description="The time taken for the delete in seconds."
    )


class Vectors(tp.NamedTuple):
    """Asynchronous client for Quipubase vector endpoints."""

    client: AsyncClient

    async def list(self, *, namespace: str) -> tp.List[str]:
        """
        Get all IDs from a specific namespace.

        Args:
            namespace: The namespace to retrieve IDs from.

        Returns:
            A list of all IDs (strings) within the namespace.
        """
        response = await self.client.get(f"/vector/{namespace}")
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return tp.cast(tp.List[str], data)

    async def retrieve(self, *, namespace: str, id: str) -> tp.List[Embedding]:
        """
        Get a specific vector by its ID from a namespace.

        Args:
            namespace: The namespace to get the vector from.
            id: The unique identifier of the vector.

        Returns:
            The raw JSON data for the requested vector.
        """
        response = await self.client.get(f"/vector/{namespace}/{id}")
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return [Embedding(**item) for item in data]

    async def upsert(
        self, *, namespace: str, **kwargs: tpe.Unpack[EmbedText]
    ) -> UpsertResponse:
        """
        Upsert texts into the vector store.

        This method inserts new texts or updates existing ones, converting them
        to vector embeddings.

        Args:
            namespace: The namespace to upsert the texts into.
            request: An EmbedText object containing the texts to upsert.

        Returns:
            An UpsertResponse object.
        """
        response = await self.client.post(f"/vector/{namespace}", json=kwargs)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return UpsertResponse(**data)

    async def query(
        self, *, namespace: str, **kwargs: tpe.Unpack[QueryText]
    ) -> QueryResponse:
        """
        Query the vector store for similar texts.

        Args:
            namespace: The namespace to query.
            request: A QueryText object containing the query details.

        Returns:
            A QueryResponse object containing the matched texts and their scores.
        """
        response = await self.client.put(f"/vector/{namespace}", json=kwargs)
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return QueryResponse(**data)

    async def delete(self, *, namespace: str, ids: tp.List[str]) -> DeleteResponse:
        """
        Delete embeddings from the vector store by their IDs.

        Args:
            namespace: The namespace to delete embeddings from.
            ids: A list of IDs to delete.

        Returns:
            A DeleteResponse object with the count and IDs of the deleted embeddings.
        """
        response = await self.client.delete(f"/vector/{namespace}", params={"ids": ids})
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return DeleteResponse(**data)
