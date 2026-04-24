from typing import Any

from mcp.server.fastmcp import FastMCP

from meta_insights_mcp.meta_client import MetaClient


def register(mcp: FastMCP, get_client) -> None:
    @mcp.tool()
    async def list_meta_assets() -> dict[str, Any]:
        """List Meta business assets visible to the current access token.

        Returns ad accounts, Pages, and Instagram business accounts the token
        has been granted access to. Use this first to discover IDs to pass
        into the other tools.
        """
        client: MetaClient = get_client()
        me = await client.get("/me", {"fields": "id,name"})
        ad_accounts = await client.get(
            "/me/adaccounts",
            {"fields": "id,account_id,name,currency,account_status"},
            paginate=True,
        )
        pages = await client.get(
            "/me/accounts",
            {"fields": "id,name,category,tasks"},
            paginate=True,
        )
        return {
            "user": me,
            "ad_accounts": ad_accounts.get("data", []),
            "pages": pages.get("data", []),
        }

    @mcp.tool()
    async def check_token_status() -> dict[str, Any]:
        """Inspect the current Meta access token (expiry, scopes, app, user).

        Uses the Graph API `debug_token` endpoint. Helpful when a tool
        returns a permissions error — confirms what the token can actually do.
        """
        client: MetaClient = get_client()
        return await client.get(
            "/debug_token",
            {"input_token": client._settings.access_token},  # noqa: SLF001
        )
