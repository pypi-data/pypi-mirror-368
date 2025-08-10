from hmac import new
from hashlib import sha1
from base64 import b64encode
from secrets import token_bytes
from typing import ClassVar, Any
from aiohttp import ClientSession

from ._helpers import jsonify


__all__ = ["ElderCrypt"]

class ElderCrypt:
    __slots__ = (
        "_headers",
        "_aiohttp_session"
    )

    PREFIX: ClassVar[bytes] = b'\x52'
    DEVICE_KEY: ClassVar[bytes] = bytes.fromhex("AE49550458D8E7C51D566916B04888BFB8B3CA7D") 
    SIGNATURE_KEY: ClassVar[bytes] = bytes.fromhex("EAB4F1B9E3340CD1631EDE3B587CC3EBEDF1AFA9")

    def __init__(self, key: str) -> None:
        self._aiohttp_session: ClientSession | None = None
        self._headers: dict[str, str] = {
            "Connection": "Keep-Alive",
            "Authorization": key,
            "Content-Type": "application/json",
            "Accept-Encoding": "gzip, deflate, br"
        }

    def signature(self, data: str | bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")

        digest = new(self.SIGNATURE_KEY, data, sha1).digest()
        signature = bytes([self.PREFIX[0]]) + digest

        return b64encode(signature).decode("utf-8")

    def create_device(self) -> str:
        random_bytes = token_bytes(20)
        data = self.PREFIX + sha1(random_bytes).digest()

        digest = new(self.DEVICE_KEY, data, sha1).hexdigest()
        return f"{data.hex()}{digest}".upper()

    async def _create_aiohttp_session(self) -> ClientSession:
        if not self._aiohttp_session or self._aiohttp_session.closed:
            self._aiohttp_session = ClientSession(
                base_url="https://qfhmflnp-3000.euw.devtunnels.ms",
                headers=self._headers,
            )

        return self._aiohttp_session
    
    async def signature_ecdsa(self, data: str, user_id: str) -> str:
        aiohttp_session = await self._create_aiohttp_session() 

        async with aiohttp_session.post(
            url="/api/v1/signature/ecdsa",
            data=jsonify({"payload": data, "userId": user_id})
        ) as response:
                if response.status != 200:
                    raise Exception(await response.text())
                
                return (await response.json())["ECDSA"]
    
    async def get_credentials(self, user_id: str) -> Any:
        aiohttp_session = await self._create_aiohttp_session()

        async with aiohttp_session.get(
            url=f"/api/v1/signature/credentials/{user_id}"
        ) as response:
            if response.status != 200:
                raise Exception(await response.text())
        
            return (await response.json())["credentials"]