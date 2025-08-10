from aminodorks.glyphs import LinkInfoV2
from aminodorks.arcana import cast, RelayClient


__all__ = ["LinkCitadel"]

class LinkCitadel:
    __slots__ = (
        "_relay_client",
    )

    def __init__(self, relay_client: RelayClient):
        self._relay_client: RelayClient = relay_client

    async def get_from_url(self, url: str) -> LinkInfoV2:
        response = await self._relay_client.call(
            method="GET",
            path=f"g/s/link-resolution?q={url}"
        )

        return cast(response["linkInfoV2"], LinkInfoV2)