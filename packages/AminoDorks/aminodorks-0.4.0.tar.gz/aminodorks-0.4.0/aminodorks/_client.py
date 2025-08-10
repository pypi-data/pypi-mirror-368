from aiohttp import BasicAuth

from ._community import Community
from aminodorks.glyphs import UserProfile
from aminodorks.arcana import RelayClient, HeadersManager

from aminodorks.citadel import (
    LinkCitadel,
    AuthCitadel, 
    UserCitadel, 
    MediaCitadel,
    SpaceCitadel,
    ThreadCitadel
)


__all__ = ["DorksClient"]

class DorksClient:
    __slots__ = (
        "_auth",
        "_user",
        "_link",
        "_media",
        "_space",
        "_thread",
        "_community",
        "_relay_client",
        "_headers_manager"
    )

    def __init__(
        self,
        key: str,
        *,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None
    ) -> None:
        self._headers_manager: HeadersManager = HeadersManager(key)

        self._relay_client: RelayClient = RelayClient(
            self._headers_manager, proxy=proxy, proxy_auth=proxy_auth
        )

        self._auth:         AuthCitadel    |       None = None
        self._user:         UserCitadel    |       None = None
        self._media:        MediaCitadel   |       None = None
        self._link:         LinkCitadel    |       None = None
        self._thread:       ThreadCitadel  |       None = None
        self._space:        SpaceCitadel   |       None = None
        self._community:    Community      |       None = None
    
    @property
    def sid(self) -> str | None:
        return self._headers_manager.sid
    
    @property
    def auid(self) -> str | None:
        return self._headers_manager.auid
    
    @property
    def device_id(self) -> str | None:
        return self._headers_manager.device_id
    
    @property
    def user_profile(self) -> UserProfile | None:
        return self.auth.user_profile
    
    @property
    def raise_user_profile(self) -> UserProfile:
        if self.auth.user_profile is None:
            raise Exception("UserProfile is None!")
        
        return self.auth.user_profile
    
    @property
    def auth(self) -> AuthCitadel:
        if self._auth is None:
            self._auth = AuthCitadel(self._relay_client)

        return self._auth
    
    @property
    def user(self) -> UserCitadel:
        if self._user is None:
            self._user = UserCitadel(self._relay_client)

        return self._user
    
    @property
    def media(self) -> MediaCitadel:
        if self._media is None:
            self._media = MediaCitadel(self._relay_client)

        return self._media
    
    @property
    def link(self) -> LinkCitadel:
        if self._link is None:
            self._link = LinkCitadel(self._relay_client)
        
        return self._link

    @property
    def thread(self) -> ThreadCitadel:
        if self._thread is None:
            self._thread = ThreadCitadel(self._relay_client)

        return self._thread
    
    @property
    def space(self) -> SpaceCitadel:
        if self._space is None:
            self._space = SpaceCitadel(self._relay_client)

        return self._space
    
    @property
    def community(self) -> Community:
        if self._community is None:
            raise Exception("Initialize community first!")
        
        return self._community
    
    @community.setter
    def community(self, value: int | str) -> None:
        self._community = Community(self._relay_client, f"x{value}")
    
    async def close(self) -> None:
        await self._relay_client.close()