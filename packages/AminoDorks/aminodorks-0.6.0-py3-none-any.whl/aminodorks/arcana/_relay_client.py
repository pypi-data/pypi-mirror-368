from typing import Any
from aiohttp import BasicAuth, ClientSession

from ._headers_manager import HeadersManager


__all__ = ["RelayClient"]

class RelayClient:
    __slots__ = (
        "_proxy",
        "_proxy_auth",
        "_aiohttp_session",
        "headers_manager"
    )

    def __init__(
        self,
        headers_manager: HeadersManager,
        *,
        proxy: str | None = None,
        proxy_auth: BasicAuth | None = None,
    ) -> None:
        self._proxy: str | None = proxy
        self._proxy_auth: BasicAuth | None = proxy_auth
        self._aiohttp_session: ClientSession | None = None
        self.headers_manager: HeadersManager = headers_manager

    async def _create_aiohttp_session(self) -> ClientSession:
        if not self._aiohttp_session or self._aiohttp_session.closed:
            self._aiohttp_session = ClientSession(
                proxy=self._proxy,
                proxy_auth=self._proxy_auth,
                base_url="https://service.aminoapps.com/api/v1/"
            )

        return self._aiohttp_session
    
    async def close(self) -> None:
        if self._aiohttp_session and not self._aiohttp_session.closed:
            await self._aiohttp_session.close()

    async def call(
        self,
        method: str,
        path:str,
        *,
        data: str | bytes | None = None,
        content_type: str | None = None,
    ) -> Any:
        aiohttp_session = await self._create_aiohttp_session()
        
        async with aiohttp_session.request(
            url=path,
            method=method, 
            data=data, 
            headers=await self.headers_manager.get_headers(data, content_type)
        ) as response:
            if response.status != 200:
                await self.close()
                raise Exception(await response.text(), response.status)  #TODO: MAKE EXCEPTIONS FOR THIS CLASS AND FOR ELDERCRYPT
            
            return await response.json()
