from typing import Any
from msgspec import Struct, field


__all__ = [
    "Ads",
    "Author",
    "Account",
    "LinkInfo",
    "LinkInfoV2",
    "DeviceInfo",
    "Extensions",
    "PopupConfig",
    "UserProfile",
    "AdvancedSettings",
    "LinkInfoExtensions"
]


class AdvancedSettings(Struct):
    analytics_enabled : int = field(name="analyticsEnabled")


class DeviceInfo(Struct):
    last_client_type : int = field(name="lastClientType")


class Ads(Struct):
    status          : int
    last_popup_time : str = field(name="lastPopupTime")


class PopupConfig(Struct):
    ads : Ads

class Extensions(Struct):
    content_language                    : str               = field(name="contentLanguage")
    ads_flags                           : int               = field(name="adsFlags")
    ads_level                           : int               = field(name="adsLevel")
    device_info                         : DeviceInfo        = field(name="deviceInfo")
    popup_config                        : PopupConfig       = field(name="popupConfig")
    media_lab_ads_migration_august2020  : bool              = field(name="mediaLabAdsMigrationAugust2020")
    ads_enabled                         : bool              = field(name="adsEnabled")

class Author(Struct):
    status                     : int          = field(name="status")
    is_nickname_verified       : bool         = field(name="isNicknameVerified")
    uid                        : str          = field(name="uid")
    level                      : int          = field(name="level")
    following_status           : int          = field(name="followingStatus")
    account_membership_status  : int          = field(name="accountMembershipStatus")
    is_global                  : bool         = field(name="isGlobal")
    membership_status          : int          = field(name="membershipStatus")
    reputation                 : int          = field(name="reputation")
    role                       : int          = field(name="role")
    amino_id                   : str          = field(name="aminoId")
    ndc_id                     : int          = field(name="ndcId")
    members_count              : int          = field(name="membersCount")
    nickname                   : str          = field(name="nickname")
    icon                       : str | None   = field(name="icon", default=None)

class UserProfile(Struct):
    mood_sticker                        : str           | None  = field(name="moodSticker")
    items_count                         : int                   = field(name="itemsCount")
    consecutive_check_in_days           : int           | None  = field(name="consecutiveCheckInDays")
    uid                                 : str
    modified_time                       : str           | None  = field(name="modifiedTime")
    following_status                    : int                   = field(name="followingStatus")
    online_status                       : int                   = field(name="onlineStatus")
    account_membership_status           : int                   = field(name="accountMembershipStatus")
    is_global                           : bool                  = field(name="isGlobal")
    reputation                          : int
    posts_count                         : int                   = field(name="postsCount")
    members_count                       : int                   = field(name="membersCount")
    nickname                            : str
    media_list                          : list[Any]     | None  = field(name="mediaList")
    icon                                : str           | None
    is_nickname_verified                : bool                  = field(name="isNicknameVerified")
    mood                                : str           | None
    level                               : int
    notification_subscription_status    : int                   = field(name="notificationSubscriptionStatus")
    push_enabled                        : bool          | None  = field(name="pushEnabled")
    membership_status                   : int                   = field(name="membershipStatus")
    content                             : str           | None
    joined_count                        : int                   = field(name="joinedCount")
    role                                : int
    comments_count                      : int                   = field(name="commentsCount")
    amino_id                            : str                   = field(name="aminoId")
    ndc_id                              : int                   = field(name="ndcId")
    created_time                        : str                   = field(name="createdTime")
    extensions                          : dict[Any, Any] | None
    stories_count                       : int                   = field(name="storiesCount")
    blogs_count                         : int                   = field(name="blogsCount")
    status                              : int           | None  = field(default=None)

class UserProfileList(Struct):
    user_profile_list: list[UserProfile] = field(name="userProfileList")

class Account(Struct):
    username                : str       | None
    status                  : int
    uid                     : str
    modified_time           : str                = field(name="modifiedTime")
    twitter_id              : str       | None   = field(name="twitterID")
    activation              : int
    phone_number_activation : int                = field(name="phoneNumberActivation")
    email_activation        : int                = field(name="emailActivation")
    apple_id                : str       | None   = field(name="appleID")
    facebook_id             : str       | None   = field(name="facebookID")
    nickname                : str
    media_list              : list[Any] | None   = field(name="mediaList")
    google_id               : str                = field(name="googleID")
    icon                    : str       | None
    security_level          : int                = field(name="securityLevel")
    phone_number            : str       | None   = field(name="phoneNumber")
    membership              : Any       | None
    advanced_settings       : AdvancedSettings   = field(name="advancedSettings")
    role                    : int
    amino_id_editable       : bool               = field(name="aminoIdEditable")
    amino_id                : str                = field(name="aminoId")
    created_time            : str                = field(name="createdTime")
    extensions              : Extensions
    email                   : str

class LinkInfo(Struct):
    object_id:      str      =      field(name="objectId")
    target_code:    int      =      field(name="targetCode")
    ndc_id:         int      =      field(name="ndcId")
    full_path:      str | None      =      field(name="fullPath")
    short_code:     Any      =      field(name="shortCode")
    object_type:    int      =      field(name="objectType")

class LinkInfoExtensions(Struct):
    link_info: LinkInfo = field(name="linkInfo")

class LinkInfoV2(Struct):
    path:       str | None
    extensions: LinkInfoExtensions