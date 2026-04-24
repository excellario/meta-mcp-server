import logging
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from meta_insights_mcp.config import load_settings
from meta_insights_mcp.meta_client import MetaClient
from meta_insights_mcp.tools import register_ads, register_assets, register_business, register_pages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

_client: MetaClient | None = None


@asynccontextmanager
async def lifespan(_: FastMCP):
    global _client
    settings = load_settings()
    _client = MetaClient(settings)
    try:
        yield {}
    finally:
        await _client.aclose()
        _client = None


def _get_client() -> MetaClient:
    if _client is None:
        raise RuntimeError("Meta client not initialized — server lifespan did not start.")
    return _client


mcp = FastMCP(
    "meta-insights",
    instructions=(
        "Tools for reading Meta (Facebook / Instagram) business insights via the "
        "Graph and Marketing APIs. Call `list_meta_assets` first to discover the "
        "ad account and Page IDs available to the configured access token."
    ),
    lifespan=lifespan,
)

register_assets(mcp, _get_client)
register_ads(mcp, _get_client)
register_pages(mcp, _get_client)

import os

if os.getenv("META_BUSINESS_ID", "").strip():
    register_business(mcp, _get_client)
    logging.getLogger("meta_mcp").info("Business tools enabled (META_BUSINESS_ID set).")
else:
    logging.getLogger("meta_mcp").info(
        "Business tools disabled — set META_BUSINESS_ID to enable."
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
