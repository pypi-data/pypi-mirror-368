from typing import Any

from httpx import AsyncClient, Response


class HTTPClient:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def post(self, url: str, json: Any | None = None) -> Response:
        return await self.client.post(url=url, json=json)

    async def patch(self, url: str, json: Any | None = None) -> Response:
        return await self.client.patch(url=url, json=json)
