from time import time
from typing import Any, Literal

from aminodorks.glyphs import (
    CommentList,
    UserProfile, 
    CommentGlyph,
    UserProfileList
)

from aminodorks.arcana import (
    cast,
    jsonify,
    RelayClient, 
)


__all__ = ["UserCitadel"]

class UserCitadel:
    __slots__ = (
        "_ndc_id",
        "_relay_client"
    )

    def __init__(self, relay_client: RelayClient, ndc_id: str = "g") -> None:
        self._ndc_id: str = ndc_id
        self._relay_client: RelayClient = relay_client
    
    @property
    def auid(self) -> str | None:
        return self._relay_client.headers_manager.auid

    async def get_user_info(self, user_id: str) -> UserProfile:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/user-profile/{user_id}"
        )
        return cast(response["userProfile"], UserProfile)
    
    async def get_user_following(self, user_id: str, start: int = 0, size: int = 100) -> list[UserProfile]:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/user-profile/{user_id}/joined?start={start}&size={size}"
        )

        return cast(response, UserProfileList).user_profile_list
    
    async def get_user_followers(self, user_id: str, start: int = 0, size: int = 100) -> list[UserProfile]:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/user-profile/{user_id}/member?start={start}&size={size}"
        )

        return cast(response, UserProfileList).user_profile_list
    
    async def get_user_visitors(self, user_id: str, start: int = 0, size: int = 100) -> Any:
        return await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/user-profile/{user_id}/visitors?start={start}&size={size}"
        )
    
    async def get_blocked_users(self, start: int = 0, size: int = 100) -> list[UserProfile]:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/block?start={start}&size={size}"
        )

        return cast(response, UserProfileList).user_profile_list
    
    async def get_wall_comments(
            self, 
            user_id: str, 
            sorting: Literal["newest", "top", "oldest"], 
            start: int = 0, 
            size: int = 100
    ) -> list[CommentGlyph]:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/user-profile/{user_id}/g-comment?sort={sorting}&start={start}&size={size}"
        )

        return cast(response, CommentList).comment_list
    
    async def visit(self, user_id: str) -> int:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/user-profile/{user_id}?action=visit"
        )

        return response["api:statuscode"]
    
    async def follow(self, user_id: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/user-profile/{user_id}/member",
            content_type="application/x-www-form-urlencoded"
        )

        return response["api:statuscode"]
    
    async def follow_list(self, user_ids: list[str]) -> int:
        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/user-profile/{self.auid}/joined",
            data=jsonify({
                "targetUidList": user_ids,
                "timestamp": int(time() * 1000)
            })
        )

        return response["api:statuscode"]
    
    async def unfollow(self, user_id: str) -> int:
        response = await self._relay_client.call(
            method="DELETE",
            path=f"{self._ndc_id}/s/user-profile/{user_id}/member/{self.auid}"
        )

        return response["api:statuscode"]