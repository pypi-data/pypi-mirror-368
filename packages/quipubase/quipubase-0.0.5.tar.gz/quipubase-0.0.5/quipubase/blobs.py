# quipubase/files/client.py
#
# Asynchronous client for Quipubase file endpoints.

# quipubase/files/typedefs.py
#
# Pydantic models for Quipubase Files API responses.

from __future__ import annotations

import json
import typing as tp

import typing_extensions as tpe
from httpx import AsyncClient
from loguru import logger

from ._base import Base

FileContent = tp.Union[tp.IO[bytes], bytes, str]
FileTypes: tpe.TypeAlias = tp.Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    tp.Tuple[tp.Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    tp.Tuple[tp.Optional[str], FileContent, tp.Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    tp.Tuple[tp.Optional[str], FileContent, tp.Optional[str], tp.Mapping[str, str]],
]


# --- Files API Response Models ---
class ChunkFile(Base):
    """Model for a chunked file."""

    chunks: list[str]
    created: float
    chunkedCount: int


class FileType(Base):
    """Model for a file type."""

    url: str
    path: str


class GetOrCreateFile(Base):
    """Model for a get or create file."""

    data: FileType
    created: float


class DeleteFile(Base):
    """Model for a delete file."""

    deleted: bool


class TreeNode(Base):
    """Model for a tree node."""

    type: tp.Literal["file", "folder"]
    name: str
    path: str
    content: str | list[TreeNode]


class Blobs(tp.NamedTuple):
    """Asynchronous client for Quipubase file endpoints."""

    client: AsyncClient

    async def chunk(
        self, *, file: FileTypes, format: tp.Literal["html", "text"]
    ) -> ChunkFile:
        """
        Uploads a file and chunks it.

        Args:
                files: The file data to upload.
                format: The format of the file, "html" or "text".

        Returns:
                A ChunkFile object with a success message and file ID.
        """
        response = await self.client.post(
            "/blob", params={"format": format}, files={"file": file}
        )
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return ChunkFile(**data)

    async def create(
        self, *, path: str, file: FileTypes, bucket: str = "quipu-store"
    ) -> GetOrCreateFile:
        """
        Uploads a file and creates a new one at the specified path.

        Args:
                path: The path of the file.
                files: The file data to upload.
                bucket: The bucket to store the file in.

        Returns:
                A GetOrCreateFile object.
        """
        response = await self.client.put(
            f"/blob/{path}", params={"bucket": bucket}, files={"file": file}
        )
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return GetOrCreateFile(**data)

    async def delete(self, *, path: str, bucket: str = "quipu-store") -> DeleteFile:
        """
        Deletes a file at the specified path.

        Args:
                path: The path of the file to delete.
                bucket: The bucket the file is in.

        Returns:
                A DeleteFile object indicating success.
        """
        response = await self.client.delete(f"/blob/{path}", params={"bucket": bucket})
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return DeleteFile(**data)

    async def retrieve(
        self, *, path: str, bucket: str = "quipu-store"
    ) -> GetOrCreateFile:
        """
        Gets a file at the specified path.

        Args:
                path: The path of the file.
                bucket: The bucket the file is in.

        Returns:
                A GetOrCreateFile object.
        """
        response = await self.client.get(f"/blob/{path}", params={"bucket": bucket})
        response.raise_for_status()
        data = response.json()
        logger.info(data)
        return GetOrCreateFile(**data)

    async def list(self, *, path: str, bucket: str = "quipu-store") -> tp.Any:
        """
        Gets the file tree for a given path.

        Args:
                path: The path to get the file tree from.
                bucket: The bucket to look in.

        Returns:
                The raw JSON data of the file tree.
        """
        async with self.client.stream(
            "GET", f"/blobs/{path}", params={"bucket": bucket}
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_lines():
                data = chunk[6:]
                yield FileType(**json.loads(data))  # type: ignore
