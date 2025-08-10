from aminodorks.glyphs import CommunityList
from aminodorks.arcana import cast, RelayClient


__all__ = ["SpaceCitadel"]

class SpaceCitadel:
    __slots__ = ("_relay_client",)

    def __init__(self, relay_client: RelayClient) -> None:
        self._relay_client: RelayClient = relay_client

    async def joined_communities(self, start: int = 0, size: int = 100) -> CommunityList:
        response = await self._relay_client.call(
            method="GET",
            path=f"g/s/community/joined?v=1&start={start}&size={size}"
        )

        return cast(response, CommunityList)