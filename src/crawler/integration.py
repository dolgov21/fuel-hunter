from src.crawler.client import Client
from src.crawler.schemas import CommentResponseSchema
from src.core.config import GDE_BENZ_BASE_URL


class GdeBenzIntegration:
    def __init__(self, client: Client, base_url: str = GDE_BENZ_BASE_URL):
        self._client = client
        self._base_url = base_url

    async def get_external_status(self, osm_id: str) -> CommentResponseSchema:
        response = await self._client.request(
            "GET", f"{self._base_url.rstrip('/')}/api/v1/stations/{osm_id}"
        )
        return CommentResponseSchema.model_validate(response.json())
