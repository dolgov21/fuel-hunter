from typing import Literal

from httpx import AsyncClient, Response


class Client:
    async def __aenter__(self):
        self.client = AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.aclose()

    async def request(
        self, method: Literal["GET", "POST", "PUT", "DELETE"], url: str, **kwargs
    ) -> Response:
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response