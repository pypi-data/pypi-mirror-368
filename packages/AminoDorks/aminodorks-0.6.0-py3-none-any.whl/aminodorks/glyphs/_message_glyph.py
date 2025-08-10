from typing import Any
from msgspec import Struct, field

from ._additional import Author


__all__ = ["MessageGlyph", "MessageList", "MessagePaging"]

class MessageGlyph(Struct):
    included_in_summary:      bool | None = field(default=None, name="includedInSummary")
    uid:                      str  | None = field(default=None, name="uid")
    author:                   Author | None = field(default=None, name="author")
    is_hidden:                bool | None= field(default=None, name="isHidden")
    message_id:               str | None = field(default=None, name="messageId")
    media_type:               int | None = field(default=None, name="mediaType")
    content:                  str | None = field(default=None, name="content")
    client_ref_id:            int | None = field(default=None, name="clientRefId")
    thread_id:                str | None = field(default=None, name="threadId")
    created_time:             str | None = field(default=None, name="createdTime")
    extensions:               dict[str, Any] | None = field(default=None, name="extensions")
    type:                     int | None = field(default=None, name="type")
    media_value:              Any | None = field(default=None, name="mediaValue")

class MessagePaging(Struct):
    next_page_token:          str | None = field(default=None, name="nextPageToken")
    prev_page_token:          str | None = field(default=None, name="prevPageToken")

class MessageList(Struct):
    message_list:             list[MessageGlyph] | None = field(default=None, name="messageList")
    paging:                   MessagePaging | None = field(default=None, name="paging")
    api_message:              str | None = field(default=None, name="api:message")
    api_statuscode:           int | None = field(default=None, name="api:statuscode")
    api_duration:             str | None = field(default=None, name="api:duration")
    api_timestamp:            str | None = field(default=None, name="api:timestamp")