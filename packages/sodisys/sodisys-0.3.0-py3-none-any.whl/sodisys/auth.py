from attr import dataclass
from abc import ABC
from aiohttp import ClientSession


@dataclass
class SodisysSession:
    jwt_token: str


class SodisysAuthorization(ABC):
    session: ClientSession
    _sodisys_session: SodisysSession | None = None

    def __init__(self, session: ClientSession) -> None:
        self.session = session

    async def authorize(self, username: str, password: str) -> None:
        params = {
            "username": username,
            "password": password,
        }

        response = await self.session.post(
            "https://appapi.app.sodisys.eu/public/a/login", json=params
        )
        response_json = await response.json()
        token = response_json["jwt_token"]

        self._sodisys_session = SodisysSession(token)

    def get_access_token(self) -> str:
        if not self._sodisys_session:
            raise NotAuthorizedError

        return self._sodisys_session.jwt_token


class NotAuthorizedError(Exception):
    """Not authorized.

    Did you forget to call Authorization.authorize()?
    """
