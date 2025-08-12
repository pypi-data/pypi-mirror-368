import logging
from aiohttp import ClientSession

from sodisys.rest_api import RestApi
from sodisys.auth import SodisysAuthorization
from sodisys.rest_api.model.live import LiveResponse
from sodisys.rest_api.model.data import DataResponse

_LOGGER = logging.getLogger(__name__)


class Sodisys:
    session: ClientSession
    authorization: SodisysAuthorization
    rest_api: RestApi

    def __init__(self, session: ClientSession) -> None:
        self.session = session
        self.authorization = SodisysAuthorization(session)
        self.rest_api = RestApi(session, self.authorization)

    async def login(self, username: str, password: str) -> None:
        await self.authorization.authorize(username, password)
        _LOGGER.debug("authorization successful.")

    async def get_live(self) -> LiveResponse:
        return await self.rest_api.get_live()

    async def get_data(self) -> DataResponse:
        return await self.rest_api.get_data()
