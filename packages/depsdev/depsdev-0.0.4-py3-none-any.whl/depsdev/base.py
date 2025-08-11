from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from urllib.parse import quote

import httpx

if TYPE_CHECKING:
    from httpx._types import QueryParamTypes
    from typing_extensions import Literal

    from depsdev.v3 import Incomplete

logger = logging.getLogger(__name__)


@dataclass
class BaseClient:
    base_url: str
    timeout: float = 5.0
    client: httpx.AsyncClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def _requests(
        self,
        url: str = "",
        method: Literal["GET", "POST"] = "GET",
        params: QueryParamTypes | None = None,
        json: object | None = None,
    ) -> Incomplete:
        logger.info(locals())
        response = await self.client.request(method=method, url=url, params=params, json=json)
        if not response.is_success:
            logger.error(
                "Request failed with status code %s: %s", response.status_code, response.text
            )
            response.raise_for_status()
        return response.json()

    @staticmethod
    def url_escape(string: str) -> str:
        return quote(string, safe="")
