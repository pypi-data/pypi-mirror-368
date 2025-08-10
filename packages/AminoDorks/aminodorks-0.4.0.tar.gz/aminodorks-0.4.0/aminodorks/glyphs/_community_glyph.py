from typing import Any
from msgspec import Struct, field

__all__ = ["CommunityGlyph", "CommunityList", "CommunityAgent", "CommunityThemePack", "CommunityPaging", "UserProfile", "UserInfoInCommunities"]

class CommunityAgent(Struct):
    status:                   int  | None = field(default=None, name="status")
    is_nickname_verified:     bool | None = field(default=None, name="isNicknameVerified")
    uid:                      str |  None = field(default=None, name="uid")
    level:                    int | None  = field(default=None, name="level")
    following_status:         int | None  = field(default=None, name="followingStatus")
    account_membership_status:int | None  = field(default=None, name="accountMembershipStatus")
    is_global:                bool | None = field(default=None, name="isGlobal")
    membership_status:        int | None  = field(default=None, name="membershipStatus")
    reputation:               int | None  = field(default=None, name="reputation")
    role:                     int | None  = field(default=None, name="role")
    ndc_id:                   int | None  = field(default=None, name="ndcId")
    members_count:            int | None  = field(default=None, name="membersCount")
    nickname:                 str | None  = field(default=None, name="nickname")
    icon:                     str | None  = field(default=None, name="icon")

class CommunityThemePack(Struct):
    theme_color:              str | None = field(default=None, name="themeColor")
    theme_pack_hash:          str | None = field(default=None, name="themePackHash")
    theme_pack_revision:      int | None = field(default=None, name="themePackRevision")
    theme_pack_url:           str | None = field(default=None, name="themePackUrl")

class CommunityGlyph(Struct):
    user_added_topic_list:    Any        = field(default=None, name="userAddedTopicList")
    agent:                    CommunityAgent | None = field(default=None, name="agent")
    listed_status:            int | None = field(default=None, name="listedStatus")
    probation_status:         int | None = field(default=None, name="probationStatus")
    theme_pack:               CommunityThemePack | None = field(default=None, name="themePack")
    members_count:            int | None = field(default=None, name="membersCount")
    primary_language:         str | None = field(default=None, name="primaryLanguage")
    community_heat:           int | None = field(default=None, name="communityHeat")
    strategy_info:            str | None = field(default=None, name="strategyInfo")
    tagline:                  str | None = field(default=None, name="tagline")
    join_type:                int | None = field(default=None, name="joinType")
    status:                   int | None = field(default=None, name="status")
    modified_time:            str | None = field(default=None, name="modifiedTime")
    ndc_id:                   int | None = field(default=None, name="ndcId")
    active_info:              dict[str, Any] | None = field(default=None, name="activeInfo")
    link:                     str | None = field(default=None, name="link")
    icon:                     str | None = field(default=None, name="icon")
    updated_time:             str | None = field(default=None, name="updatedTime")
    endpoint:                 str | None = field(default=None, name="endpoint")
    name:                     str | None = field(default=None, name="name")
    template_id:              int | None = field(default=None, name="templateId")
    created_time:             str | None = field(default=None, name="createdTime")
    promotional_media_list:   Any        = field(default=None, name="promotionalMediaList")
    launch_page:              dict[str, Any] | None = field(default=None, name="launchPage")

class CommunityPaging(Struct):
    next_page_token:          str | None = field(default=None, name="nextPageToken")
    prev_page_token:          str | None = field(default=None, name="prevPageToken")

class UserProfile(Struct):
    status:                   int | None = field(default=None, name="status")
    is_nickname_verified:     bool | None= field(default=None, name="isNicknameVerified")
    uid:                      str | None = field(default=None, name="uid")
    level:                    int | None = field(default=None, name="level")
    following_status:         int | None = field(default=None, name="followingStatus")
    account_membership_status:int | None = field(default=None, name="accountMembershipStatus")
    is_global:                bool | None= field(default=None, name="isGlobal")
    membership_status:        int | None = field(default=None, name="membershipStatus")
    reputation:               int | None = field(default=None, name="reputation")
    role:                     int | None = field(default=None, name="role")
    ndc_id:                   int | None = field(default=None, name="ndcId")
    members_count:            int | None = field(default=None, name="membersCount")
    nickname:                 str | None = field(default=None, name="nickname")
    icon:                     str | None = field(default=None, name="icon")
    avatar_frame_id:          str | None = field(default=None, name="avatarFrameId")

class UserInfoInCommunities(Struct):
    user_profile:             UserProfile | None = field(default=None, name="userProfile")

class CommunityList(Struct):
    community_list:           list[CommunityGlyph] = field(name="communityList")
    user_info_in_communities: dict[str, UserInfoInCommunities] = field(name="userInfoInCommunities")