from msgspec import Struct, field


__all__ = ["SID"]

class SID(Struct):
    signature:      str | None
    prefix:         str | None
    original:       str | None 
    payload:        str | None 
    version:        int | None   =   field(name="0")
    auid:           str    =   field(name="2")
    ip:             str | None   =   field(name="4")
    make_time:      int | None   =   field(name="5")
    client_type:    int | None   =   field(name="6")