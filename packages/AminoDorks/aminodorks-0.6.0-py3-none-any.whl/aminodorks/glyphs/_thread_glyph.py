from typing import Any
from msgspec import Struct, field


__all__ = [
    "ThreadGlyph", 
    "ThreadList", 
    "Member", 
    "MemberList", 
    "MembersSummary", 
    "Extensions",
    "AuthorGlyph",
    "LastMessageSummary"
]

class MembersSummary(Struct):
    status:            int                  = field(default=None, name="status")
    uid:               str                  = field(default=None, name="uid")
    membership_status: int                  = field(default=None, name="membershipStatus")
    role:              int                  = field(default=None, name="role")
    nickname:          str                  = field(default=None, name="nickname")
    icon:              str | None           = field(default=None, name="icon")

class Extensions(Struct):
    announcement:      str | None           = field(default=None, name="announcement")
    co_host:           list[Any] | None     = field(default=None, name="coHost")
    view_only:         bool | None          = field(default=None, name="viewOnly")
    last_members_summary_update_time: int | None = field(default=None, name="lastMembersSummaryUpdateTime")
    channel_type:      int | None           = field(default=None, name="channelType")
    bm:                list[Any] | None     = field(default=None, name="bm")

class AuthorGlyph(Struct):
    status:            int                  = field(default=None, name="status")
    is_nickname_verified: bool | None       = field(default=None, name="isNicknameVerified")
    uid:               str                  = field(default=None, name="uid")
    level:             int | None           = field(default=None, name="level")
    following_status:  int | None           = field(default=None, name="followingStatus")
    account_membership_status: int | None   = field(default=None, name="accountMembershipStatus")
    is_global:         bool | None          = field(default=None, name="isGlobal")
    membership_status: int | None           = field(default=None, name="membershipStatus")
    reputation:        int | None           = field(default=None, name="reputation")
    role:              int | None           = field(default=None, name="role")
    amino_id:          str | None           = field(default=None, name="aminoId")
    ndc_id:            int | None           = field(default=None, name="ndcId")
    members_count:     int | None           = field(default=None, name="membersCount")
    nickname:          str | None           = field(default=None, name="nickname")
    icon:              str | None           = field(default=None, name="icon")

class LastMessageSummary(Struct):
    uid:               str                  = field(default=None, name="uid")
    type:              int                  = field(default=None, name="type")
    media_type:        int | None           = field(default=None, name="mediaType")
    content:           str | None           = field(default=None, name="content")
    message_id:        str | None           = field(default=None, name="messageId")
    created_time:      str | None           = field(default=None, name="createdTime")
    is_hidden:         bool | None          = field(default=None, name="isHidden")
    media_value:       Any | None           = field(default=None, name="mediaValue")

class ThreadGlyph(Struct):
    user_added_topic_list: list[Any] | None = field(name="userAddedTopicList")
    uid:               str                  = field(name="uid")
    members_quota:     int | None           = field(name="membersQuota")
    members_summary:   list[MembersSummary] = field(name="membersSummary")
    thread_id:         str                  = field(name="threadId")
    keywords:          Any | None           = field(name="keywords")
    members_count:     int | None           = field(name="membersCount")
    strategy_info:     str | None           = field(name="strategyInfo")
    is_pinned:         bool | None          = field(name="isPinned")
    title:             str | None           = field(name="title")
    membership_status: int | None           = field(name="membershipStatus")
    content:           str | None           = field(name="content")
    need_hidden:       bool | None          = field(name="needHidden")
    alert_option:      int | None           = field(name="alertOption")
    last_read_time:    str | None           = field(name="lastReadTime")
    type:              int | None           = field(name="type")
    status:            int | None           = field(name="status")
    modified_time:     str | None           = field(name="modifiedTime")
    last_message_summary: LastMessageSummary | None = field(name="lastMessageSummary")
    condition:         int | None           = field(name="condition")
    icon:              str | None           = field(name="icon")
    latest_activity_time: str | None        = field(name="latestActivityTime")
    author:            AuthorGlyph | None   = field(name="author")
    extensions:        Extensions | None    = field(name="extensions")
    ndc_id:            int | None           = field(name="ndcId")
    created_time:      str | None           = field(name="createdTime")

class ThreadList(Struct):
    thread_list:       list[ThreadGlyph]    = field(name="threadList")

class Member(Struct):
    status:                 int 
    is_nickname_verified:   bool    =   field(name="isNicknameVerified")
    uid:                    str     
    level:                  int
    account_membership:     int     =   field(name="accountMembershipStatus")
    reputation:             int
    role:                   int
    nickname:               str
    icon:                   str | None

class MemberList(Struct):
    member_list: list[Member] = field(name="memberList")