import asyncio
import logging
from typing import Any

import httpx

from .config import Settings

logger = logging.getLogger("meta_mcp.client")


class MetaAPIError(Exception):
    def __init__(self, message: str, *, code: int | None = None, subcode: int | None = None, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.subcode = subcode
        self.status = status


class MetaClient:
    """Thin async wrapper around the Meta Graph API."""

    def __init__(self, settings: Settings, *, timeout: float = 30.0):
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.graph_url,
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "MetaClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        paginate: bool = False,
        max_pages: int = 10,
    ) -> dict[str, Any]:
        """GET a Graph API path. Token is injected automatically.

        If `paginate=True`, follows `paging.next` cursors up to `max_pages`
        and concatenates `data` arrays.
        """
        merged = dict(params or {})
        merged["access_token"] = self._settings.access_token

        first = await self._request_with_retry("GET", path, params=merged)
        if not paginate or "data" not in first:
            return first

        combined = list(first.get("data", []))
        next_url = first.get("paging", {}).get("next")
        pages = 1
        while next_url and pages < max_pages:
            resp = await self._request_with_retry("GET", next_url, params=None, absolute=True)
            combined.extend(resp.get("data", []))
            next_url = resp.get("paging", {}).get("next")
            pages += 1
        return {"data": combined, "pages_fetched": pages}

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None,
        absolute: bool = False,
        attempts: int = 4,
    ) -> dict[str, Any]:
        delay = 1.0
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                if absolute:
                    resp = await self._client.request(method, url, params=params)
                else:
                    resp = await self._client.request(method, url, params=params)
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    logger.warning("Meta API %s on %s (attempt %d)", resp.status_code, _safe(url), attempt + 1)
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                return self._handle(resp)
            except httpx.RequestError as exc:
                last_exc = exc
                logger.warning("Network error calling Meta: %s (attempt %d)", exc, attempt + 1)
                await asyncio.sleep(delay)
                delay *= 2
        if last_exc:
            raise MetaAPIError(f"Network error after retries: {last_exc}") from last_exc
        raise MetaAPIError("Exhausted retries calling Meta API")

    @staticmethod
    def _handle(resp: httpx.Response) -> dict[str, Any]:
        try:
            body = resp.json()
        except ValueError:
            body = {"raw": resp.text}
        if resp.is_success:
            return body
        err = (body or {}).get("error", {}) if isinstance(body, dict) else {}
        raise MetaAPIError(
            err.get("message") or f"Meta API error (HTTP {resp.status_code})",
            code=err.get("code"),
            subcode=err.get("error_subcode"),
            status=resp.status_code,
        )


def _safe(url: str) -> str:
    """Redact access_token from URLs for logs."""
    if "access_token=" not in url:
        return url
    return url.split("access_token=")[0] + "access_token=***"
