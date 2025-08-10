from msgspec import Struct, field

from ._additional import Account, UserProfile


__all__ = ["AuthGlyph"]

class AuthGlyph(Struct):
    auid            : str
    account         : Account
    secret          : str
    api_message     : str               = field(name="api:message")
    sid             : str
    api_statuscode  : int               = field(name="api:statuscode")
    api_duration    : str               = field(name="api:duration")
    api_timestamp   : str               = field(name="api:timestamp")
    user_profile    : UserProfile       = field(name="userProfile")