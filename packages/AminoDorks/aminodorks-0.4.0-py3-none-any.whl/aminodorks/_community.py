from aminodorks.arcana import RelayClient
from aminodorks.citadel import UserCitadel, ThreadCitadel


__all__ = ["Community"]

class Community:
    __slots__ = (
        "_user",
        "_thread",
        "_ndc_id",
        "_relay_client"
    )

    def __init__(self, relay_client: RelayClient, ndc_id: str) -> None:
        self._ndc_id: str = ndc_id
        self._relay_client: RelayClient = relay_client

        self._user: UserCitadel | None = None
        self._thread: ThreadCitadel | None = None

    @property
    def user(self) -> UserCitadel:
        if self._user is None:
            self._user = UserCitadel(self._relay_client, self._ndc_id)

        return self._user
    
    @property
    def thread(self) -> ThreadCitadel:
        if self._thread is None:
            self._thread = ThreadCitadel(self._relay_client, self._ndc_id)

        return self._thread