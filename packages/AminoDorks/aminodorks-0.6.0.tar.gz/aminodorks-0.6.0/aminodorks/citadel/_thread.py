from time import time
from aiofiles import open
from base64 import b64encode
from typing import Any, Literal
from aminodorks.arcana import jsonify, cast, RelayClient

from aminodorks.glyphs import (
    Member,
    MemberList,
    ThreadList,
    ThreadGlyph,
    MessageList
)


__all__ = ["ThreadCitadel"]

class ThreadCitadel:
    __slots__ = (
        "_ndc_id",
        "_relay_client"
    )

    def __init__(self, relay_client: RelayClient, ndc_id: str = "g"):
        self._ndc_id: str = ndc_id
        self._relay_client: RelayClient = relay_client

    async def get_threads(self, start: int = 0, size: int = 100) -> list[ThreadGlyph]:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/chat/thread?type=joined-me&start={start}&size={size}"
        )

        return cast(response, ThreadList).thread_list
    
    async def get_thread(self, thread_id: str) -> ThreadGlyph:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}"
        )

        return cast(response["thread"], ThreadGlyph)
    
    async def get_thread_users(self, thread_id: str, start: int = 0, size: int = 100) -> list[Member]:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/member?start={start}&size={size}&type=default&cv=1.2"
        )

        return cast(response, MemberList).member_list
    
    async def join_thread(self, thread_id: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/member/{self._relay_client.headers_manager.auid}",
            content_type="application/x-www-form-urlencoded"
        )

        return response["api:statuscode"]
    
    async def leave_thread(self, thread_id: str) -> int:
        response = await self._relay_client.call(
            method="DELETE",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/member/{self._relay_client.headers_manager.auid}",
            content_type="application/x-www-form-urlencoded"
        )

        return response["api:statuscode"]
    
    async def create_thread(
        self,
        message: str,
        user_ids: list[str],
        title: str | None = None,
        content: str | None = None,
        is_global: bool = False,
        publish_to_global: bool = False
    ) -> int:
        data: dict[str, Any] = {
            "type": 0,
            "publishToGlobal": 0,
            "title": title,
            "inviteeUids": user_ids,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(time() * 1000)
        }

        if is_global:
            data["type"] = 2; data["eventSource"] = "GlobalComposeMenu"

        if publish_to_global:
            data["publishToGlobal"] = 1

        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread",
            data=jsonify(data)
        )

        return response["api:statuscode"]
    
    async def invite_to_thread(self, user_ids: list[str], thread_id: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/member/invite",
            data=jsonify({
                "uids": user_ids,
                "timestamp": int(time() * 1000)
            })
        )

        return response["api:statuscode"]

    async def kick(self, user_id: str, thread_id: str, allow_rejoin: int = 0) -> int:
        response = await self._relay_client.call(
            method="DELETE",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/member/{user_id}?allowRejoin={allow_rejoin}"
        )
        
        return response["api:statuscode"]

    async def get_thread_messages(self, thread_id: str, size: int = 100) -> MessageList:
        response = await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/message?v=2&pagingType=t&size={size}"
        )

        return cast(response, MessageList)
    
    async def get_message_info(self, thread_id: str, message_id: str) -> Any:
        return await self._relay_client.call(
            method="GET",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/message/{message_id}"
        )
    
    async def send_message(
        self,
        thread_id: str,
        message: str,
        message_type: int = 0,
        reply_to: str | None = None, 
        mention_user_ids: list[str] | None = None
    ) -> int:
        message = message.replace("<$", "").replace("$>", "")

        data: dict[str, Any] = {
            "type": message_type,
            "content": message,
            "clientRefId": int(time() / 10 % 1000000000),
            "extensions": {"mentionedArray": [{"uid": user_id for user_id in mention_user_ids}] if mention_user_ids else []},
            "timestamp": int(time() * 1000)
        }

        if reply_to: data["replyMessageId"] = reply_to

        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/message",
            data=jsonify(data)
        )

        return response["api:statuscode"]

    async def send_media_message(
        self,
        thread_id: str,
        file_path: str,
        file_type: Literal["audio/aac", "image/jpg", "image/gif"],
        reply_to: str | None = None 
    ) -> int:
        async with open(file_path, "rb") as file:
            _bytes = await file.read() 

        encoded = b64encode(_bytes).decode() 

        data: dict[str, Any] = {
            "type": 0,
            "content": None,
            "mediaUploadValue": encoded,
            "clientRefId": int(time() / 10 % 1000000000),
            "timestamp": int(time() * 1000)
        }

        if reply_to: data["replyMessageId"] = reply_to

        if file_type == "audio/aac":
            data.update({
                "type": 2,
                "mediaType": 110
            })

        if file_type == "image/jpg":
            data.update({
                "mediaType": 100,
                "mediaUploadValueContentType": "image/jpg",
                "mediaUhqEnabled": True
            })

        if file_type == "image/gif":
            data.update({
                "mediaType": 100,
                "mediaUploadValueContentType": "image/gif",
                "mediaUhqEnabled": True
            })

        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/message",
            data=jsonify(data)
        )

        return response["api:statuscode"]
    
    async def delete_message(self, thread_id: str, message_id: str, reason: str | None = None) -> int:
        response = await self._relay_client.call(
            method="DELETE",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/message/{message_id}",
            data=jsonify({
                "adminOpName": 102,
                "adminOpNote": {"content": reason},
                "timestamp": int(time() * 1000)
            })
        )

        return response["api:statuscode"]
    
    async def delete_message_as_staff(self, thread_id: str, message_id: str, reason: str | None = None) -> int:
        response = await self._relay_client.call(
            method="DELETE",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/message/{message_id}/admin",
            data=jsonify({
                "adminOpName": 102,
                "adminOpNote": {"content": reason},
                "timestamp": int(time() * 1000)
            })
        )

        return response["api:statuscode"]
    
    async def accept_host(self, thread_id: str, request_id: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/transfer-organizer/{request_id}/accept",
            content_type="application/x-www-form-urlencoded"
        )

        return response["api:statuscode"]
    
    async def invite_to_vc(self, thread_id: str, user_id: str) -> int:
        response = await self._relay_client.call(
            method="POST",
            path=f"{self._ndc_id}/s/chat/thread/{thread_id}/vvchat-presenter/invite",
            data=jsonify({
                "uid": user_id
            })
        )

        return response["api:statuscode"]