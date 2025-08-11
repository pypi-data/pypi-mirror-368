"""Main async client for interacting with the Spinmobile API."""

import aiohttp
from typing import Optional


class SpinmobileClient:
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        base_url: str = "https://api.spinmobile.co/",
    ):
        self.base_url = base_url.rstrip("/")
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None

    async def authenticate(self):
        """
        Authenticate the client and retrieve an access token.
        """
        url = f"{self.base_url}/api/analytics//auth/"
        payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, timeout=self.timeout
            ) as response:
                if response.status != 200:
                    raise Exception(f"Authentication failed: {response.status}")
                data = await response.json()
                self.token = data.get("token")
                if not self.token:
                    raise Exception("Authentication failed: Token not received.")

    async def get_session(self) -> aiohttp.ClientSession:
        """
        Get or create an authenticated session.
        """
        if not self.session:
            if not self.token:
                await self.authenticate()
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=self.timeout,
            )
        return self.session

    async def __aenter__(self):
        await self.get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, path: str, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with self.session.get(url, **kwargs) as resp:  # type: ignore
            resp.raise_for_status()
            return await resp.json()

    async def post(self, path: str, json=None, data=None, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with self.session.post(url, json=json, data=data, **kwargs) as resp:  # type: ignore
            resp.raise_for_status()
            return await resp.json()
