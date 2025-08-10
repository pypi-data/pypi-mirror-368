from base64 import urlsafe_b64decode
from typing import Any, Type, TypeVar

from msgspec.json import Encoder, decode
from msgspec import Struct, convert

from ..glyphs import SID


ENCODER: Encoder = Encoder()
T = TypeVar("T", bound=Struct)

def jsonify(data: Any) -> str:
    return ENCODER.encode(data).decode("utf-8")

def cast(data: Any, model: Type[T]) -> T:
    return convert(data, model)

def decode_sid(sid: str) -> SID:
    padded_sid = sid + "=" * (4 - len(sid) % 4)
    raw = urlsafe_b64decode(padded_sid)

    prefix = raw[:1].hex() 
    signature = raw[-20:].hex()
    payload = decode(raw[1:-20])

    return SID(
        original=sid,
        prefix=prefix,
        signature=signature,
        payload=str(payload),
        version=payload.get("0"),
        auid=payload.get("2"),
        ip=payload.get("4"),
        make_time=payload.get("5"),
        client_type=payload.get("6")
    )