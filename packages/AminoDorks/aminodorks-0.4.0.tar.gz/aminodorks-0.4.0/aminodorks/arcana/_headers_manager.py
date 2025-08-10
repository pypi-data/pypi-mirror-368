from typing import Any
from ._elder_crypt import ElderCrypt


__all__ = ["HeadersManager"]

class HeadersManager:
    __slots__ = (
        "_sid",
        "_auid",
        "_device_id",
        "_headers",
        "_elder_crypt"
    )

    def __init__(self, key: str) -> None:
        self._sid: str | None = None
        self._auid: str | None = None
        self._device_id: str | None = None 
        self._headers: dict[str, str] = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US",
            "Host": "service.aminoapps.com",
            "User-Agent": (
                "Dalvik/2.1.0 (Linux; U; Android 10; M2006C3MNG Build/QP1A.190711.020;"
                "com.narvii.amino.master/4.3.3121)"
            ),
            "Content-Type":  "application/json"
        }
        self._elder_crypt = ElderCrypt(key)

    def __setitem__(self, key: str, value: Any) -> None:
        if not hasattr(self, key):
            raise KeyError(f"Invalid key: {key}")
        setattr(self, key, value)
    
    def update(self, values: dict[str, Any]) -> None:
        for key, value in values.items():
            self[key] = value
    @property
    def elder_crypt(self) -> ElderCrypt:
        return self._elder_crypt
    
    @property
    def sid(self) -> str | None:
        return self._sid
    
    @property
    def auid(self) -> str | None:
        return self._auid
    
    @property
    def device_id(self) -> str | None:
        if not self._device_id:
            self.device_id = self._elder_crypt.create_device()
        
        return self._device_id
    
    
    @sid.setter
    def sid(self, value: str | None) -> None:
        self._sid = value

        if value:
            self._headers["NDCAUTH"] = f"sid={value}"
        else:
            self._headers.pop("NDCAUTH", None)

    @auid.setter
    def auid(self, value: str | None) -> None:
        self._auid = value

        if value:
            self._headers["AUID"] = value
        else:
            self._headers.pop("AUID", None)

    @device_id.setter
    def device_id(self, value: str | None) -> None:
        self._device_id = value

        if value:
            self._headers["NDCDEVICEID"] = value
        else:
            self._headers.pop("NDCDEVICEID", None)

    async def get_headers(
        self,
        data: str| bytes | None = None,
        content_type: str | None = None
    ) -> dict[str, str]:
        headers = self._headers.copy()

        if content_type:
            headers["Content-Type"] = content_type

        if data:
            headers["NDC-MSG-SIG"] = self._elder_crypt.signature(data)

            if self.auid and isinstance(data, str):
                headers["NDC-MESSAGE-SIGNATURE"] = await self._elder_crypt.signature_ecdsa(data, self.auid)

        return headers
    
    async def get_credentials(self, user_id: str) -> Any:
        return await self._elder_crypt.get_credentials(user_id)