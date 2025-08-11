# quipubase/objects/client.py
"""Objects client"""

from __future__ import annotations

import json
import typing as tp

import typing_extensions as tpe
from httpx import AsyncClient
from loguru import logger

from ._base import Base

QuipuActions: tpe.TypeAlias = tp.Literal[
    "create", "read", "update", "delete", "query", "stop"
]


class BaseModel(Base):
    """Base model"""

    def __str__(self):
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()


class SubResponse(BaseModel):
    """Event model"""

    event: QuipuActions
    data: dict[str, tp.Any] | list[dict[str, tp.Any]]


class PubResponse(BaseModel):
    """Response model"""

    collection: str
    data: dict[str, tp.Any] | list[dict[str, tp.Any]]
    event: QuipuActions


class QuipubaseRequest(tp.TypedDict):
    """
    Quipubase Request
    A model representing a request to the Quipubase API. This model includes fields for the action type, record ID, and any additional data required for the request.
    Attributes:
            event (QuipuActions): The action to be performed (create, read, update, delete, query).
            id (Optional[str]): The unique identifier for the record. If None, a new record will be created.
            data (Optional[Dict[str, Any]]): Additional data required for the request. This can include fields to update or query parameters.
    """

    event: QuipuActions
    id: tpe.NotRequired[str]
    data: tpe.NotRequired[tp.Dict[str, tp.Any]]


class Objects(tp.NamedTuple):
    """Objects client"""

    client: AsyncClient

    async def sub(self, *, collection_id: str):
        """Subscribe to a collection"""
        params = {"stream": True}
        async with self.client.stream(
            "GET", f"/collections/objects/{collection_id}", params=params
        ) as stream_response:
            async for chunk in stream_response.aiter_lines():
                try:
                    string_data = chunk[6:]
                    data = json.loads(string_data)
                    logger.info(data)
                    yield SubResponse(**data)
                except (json.JSONDecodeError, IndexError):
                    continue

    async def pub(self, *, collection_id: str, **kwargs: tpe.Unpack[QuipubaseRequest]):
        """Publish a request to a collection"""
        response = await self.client.post(
            f"/collections/objects/{collection_id}", json=kwargs
        )
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return PubResponse(**data)
