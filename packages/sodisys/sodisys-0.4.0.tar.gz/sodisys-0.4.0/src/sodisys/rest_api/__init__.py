from sodisys.auth import SodisysAuthorization
from aiohttp import ClientSession

from sodisys.rest_api.model.data import DataResponse
from sodisys.rest_api.model.live import LiveResponse


class RestApi:
    session: ClientSession
    authorization: SodisysAuthorization

    def __init__(self, session: ClientSession, authorization: SodisysAuthorization):
        self.session = session
        self.authorization = authorization

    async def get_live(self) -> LiveResponse:
        url = "https://sysapi-aws.app.sodisys.eu/sta_client/proplan/live"
        headers = self._headers()
        async with self.session.get(url, headers=headers) as response:
            return LiveResponse.model_validate_json(await response.text())

    async def get_data(self) -> DataResponse:
        url = "https://appapi.app.sodisys.eu/public/auth/sso/data"
        headers = self._headers()
        async with self.session.post(url, headers=headers) as response:
            return DataResponse.model_validate_json(await response.text())

    def _headers(self):
        return {
            "authorization": f"Bearer {self.authorization.get_access_token()}",
            "accept": "application/json",
            "referer": "https://app.sodisys.net",
            "zone": "Europe/London",
            "timezone": "UTC",
            "app-version": "1",
        }
