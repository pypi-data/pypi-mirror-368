from aiohttp import ClientSession
import json
import base64

from .exception import MidasRegistrationException
from .internal import MidasInternal

class Midas(MidasInternal):

    async def test_credentials(self) -> bool:
        """Test the provided credentials. Throws if invalid or expired."""
        return await self._test_credentials()
    
    @staticmethod
    async def register(session: ClientSession, username: str, password: str, email: str, fullname: str, organization: str | None = None) -> str:
        """
        Create a new account with the MIDAS server.
        """
        username64 = str(base64.b64encode(username.encode("utf-8")), "utf-8")
        password64 = str(base64.b64encode(password.encode("utf-8")), "utf-8")
        email64 = str(base64.b64encode(email.encode("utf-8")), "utf-8")
        fullname64 = str(base64.b64encode(fullname.encode("utf-8")), "utf-8")

        registration_info = {
            "username":username64,
            "password":password64,
            "emailaddress":email64,
            "fullname":fullname64
        }

        if (organization is not None):
            organization64 = str(base64.b64encode(organization.encode("utf-8")), "utf-8")
            registration_info["organization"] = organization64

        url = 'https://midasapi.energy.ca.gov/api/registration'
        headers =  {"Content-Type":"application/json"}

        response = await session.post(url, data=json.dumps(registration_info), headers=headers)

        if not response.ok:
            raise MidasRegistrationException(response.text)

        return await response.text()

