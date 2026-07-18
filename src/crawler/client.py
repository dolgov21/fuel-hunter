from typing import Literal

from httpx import AsyncClient, Response

from src.core.config import GDE_BENZ_BASE_URL


DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Referer": f"{GDE_BENZ_BASE_URL.rstrip('/')}/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    ),
}


class Client:
    async def __aenter__(self):
        self.client = AsyncClient(headers=DEFAULT_HEADERS)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.aclose()

    async def request(
        self, method: Literal["GET", "POST", "PUT", "DELETE"], url: str, **kwargs
    ) -> Response:
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response
