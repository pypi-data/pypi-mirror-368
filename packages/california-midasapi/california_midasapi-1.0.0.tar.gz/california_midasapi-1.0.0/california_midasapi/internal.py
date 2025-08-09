from typing import Literal, cast
from aiohttp import ClientSession, BasicAuth
import jwt
import time

from .exception import MidasAuthenticationException, MidasException

class MidasInternal():
    """Internal Methods and State used by MIDAS functionality"""
    __username: str
    __password: str
    __session: ClientSession
    __auth_token: str | None = None

    def __init__(self, session: ClientSession, username: str, password: str):
        """
        Create a new API wrapper instance using the given credentials.

        Credentials are required, if you don't have an account use the static `register` method
        """
        self.__username = username
        self.__password = password
        self.__session = session

    async def _request(self, method: Literal['GET', 'POST'], url: str):
        """Preform a request with the stored auth token and return the body."""
        if (self.__auth_token is None or not MidasInternal.__isTokenValid(self.__auth_token)):
            await self.__loginAndStore(self.__username, self.__password)
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'california-midasapi.py',
            'Authorization': "Bearer " + cast(str, self.__auth_token),
        }
        response = await self.__session.request(method, url, headers=headers)
        #TODO throw better exceptions here, maybe even retry on 401 before fully throwing
        if (not response.ok):
            raise MidasException(f"Error preforming request: {response.status} {response.text}")
        return await response.text()
    
    async def _test_credentials(self) -> bool:
        """Confirm the current stored username and password can issue a token. Throws if unsuccessful."""
        await self.__loginAndStore(self.__username, self.__password)
        return True # loginAndStore throws if unsuccessful
    
    async def __loginAndStore(self, username: str, password: str):
        '''
        Logs in with a username and password, storing the JWT token for use in future calls.
        '''
        auth = BasicAuth(username, password)
        url = 'https://midasapi.energy.ca.gov/api/token'

        response = await self.__session.get(url, auth=auth)

        if (not response.ok):
            raise MidasAuthenticationException(await response.text())

        self.__auth_token = response.headers['Token']
    
    @staticmethod
    def __isTokenValid(token: str) -> bool:
        """Return if the provided token is still valid"""
        decoded = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
        future = time.time() + 120 # 2 minutes from now
        return decoded["exp"] > future # expires more than set time from now