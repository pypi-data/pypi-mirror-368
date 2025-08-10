from aiofiles import open
from typing import Literal
from aminodorks.arcana import RelayClient


__all__ = ["MediaCitadel"]

class MediaCitadel:
    __slots__ = ("_relay_client", )

    def __init__(self, relay_client: RelayClient) -> None:
        self._relay_client: RelayClient = relay_client

    async def upload_media(self, file_path: str, file_type: Literal["audio/aac", "image/jpg"]) -> str:
        async with open(file_path, "rb") as f:
            data = await f.read()

        response = await self._relay_client.call(
            method="POST",
            path="g/s/media/upload",
            data=data,
            content_type=file_type
        )

        return response["mediaValue"]