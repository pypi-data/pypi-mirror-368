from time import time
from typing import Any

from aminodorks.glyphs import AuthGlyph, UserProfile
from aminodorks.arcana import (
    cast,
    jsonify,
    decode_sid,
    RelayClient,
    HeadersManager
)


__all__ = ["AuthCitadel"]

class AuthCitadel:
    __slots__ = (
        "user_profile",
        "_relay_client"
    )

    def __init__(self, relay_client: RelayClient) -> None:
        self.user_profile: UserProfile | None = None
        self._relay_client: RelayClient = relay_client

    @property
    def headers_manager(self) -> HeadersManager:
        return self._relay_client.headers_manager
    
    async def authenticate_with_sid(self, sid: str, device_id: str) -> None:
        decoded = decode_sid(sid) 
        update_data: dict[str, Any] = {
            "sid": sid,
            "auid": decoded.auid,
            "device_id": device_id
        }

        self.headers_manager.update(update_data)
    
    async def _public_key(self, user_id: str) -> Any:
        return await self._relay_client.call(
            method="POST",
            path="g/s/security/public_key",
            data=jsonify(await self.headers_manager.get_credentials(
                user_id
            ))
        )

    async def authenticate(self, email: str, password: str) -> AuthGlyph:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/login",
            data=jsonify({
                "email": email,
                "secret": f"0 {password}",
                "deviceID": self.headers_manager.device_id,
                "v": 2,
                "action": "normal",
                "clientType": 100,
                "timestamp": int(time() * 1000)
            })
        )

        response = cast(response, AuthGlyph)
        self.user_profile = response.user_profile
        self.headers_manager.update({
            "sid": response.sid, 
            "auid": response.auid
        })

        await self._public_key(response.auid)
        return response
    
    async def logout(self) -> int:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/logout"
        )

        self.user_profile = None
        self.headers_manager.update({
            "sid": None,
            "auid": None,
            "device_id": None
        })

        return response["api:statuscode"]
    
    async def register(
        self,
        email: str,
        password: str,
        verification_code: str,
        *,
        device_id: str | None = None,
        nickname: str = "Python AminoDorks"
    ) -> int:
        if not device_id:
            device_id = self.headers_manager.device_id

        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/register",
            data=jsonify({
                "email": email,
                "latitude": 0,
                "longitude": 0,
                "clientType": 100,
                "address": None,
                "nickname": nickname,
                "deviceID": device_id,
                "secret": f"0 {password}",
                "clientCallbackURL": "narviiapp://relogin",
                "validationContent": {
                    "data": {
                        "code": verification_code
                    },
                    "type": 1,
                    "identity": email,
                },
                "type": 1,
                "identity": email,
                "timestamp": int(time() * 1000)
            })
        )

        return response["api:statuscode"]
    
    async def verify(self, email: str, code: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/check-security-validation",
            data=jsonify({
                "validationContext": {
                    "type": 1,
                    "identity": email,
                    "data": {"code": code}
                },
                "deviceID": self.headers_manager.device_id,
                "timestamp": int(time() * 1000)
            })
        )

        return response["api:statuscode"]

    async def get_verification_code(self, email: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/request-security-validation",
            data=jsonify({
                "type": 1,
                "identity": email,
                "deviceID": self.headers_manager.device_id
            })
        )

        return response["api:statuscode"]
    
    async def activate_accout(self, email: str, code: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/activate-email",
            data=jsonify({
                "type": 1,
                "identity": email,
                "data": {"code": code},
                "deviceID": self.headers_manager.device_id
            })
        )

        return response["api:statuscode"]
    
    async def reset_password_verification_code(self, email: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/auth/request-security-validation",
            data=jsonify({
                "type": 1,
                "level": 2,
                "identity": email,
                "purpose": "reset-password",
                "deviceID": self.headers_manager.device_id
            })
        )

        return response["api:statuscode"]
    
    async def delete_accout(self, password: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path="g/s/account/delete-request",
            data=jsonify({
                "secret": f"0 {password}",
                "deviceID": self.headers_manager.device_id
            })
        )

        return response["api:statuscode"]