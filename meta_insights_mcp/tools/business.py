from typing import Any

from mcp.server.fastmcp import FastMCP

from meta_insights_mcp.meta_client import MetaClient


def _resolve_business_id(client: MetaClient, override: str | None) -> str:
    bid = (override or client._settings.business_id or "").strip()  # noqa: SLF001
    if not bid:
        raise ValueError(
            "No business_id available. Pass `business_id` to this tool, or set "
            "META_BUSINESS_ID in the server env."
        )
    return bid


def register(mcp: FastMCP, get_client) -> None:
    @mcp.tool()
    async def list_business_assets(business_id: str | None = None) -> dict[str, Any]:
        """List everything a Meta Business owns: ad accounts, Pages, IG accounts, System Users.

        Uses `META_BUSINESS_ID` from the server env when `business_id` is not passed.
        This is the business-scoped alternative to `list_meta_assets` and shows
        company-owned assets even if they are not individually assigned to the
        current System User.
        """
        client: MetaClient = get_client()
        bid = _resolve_business_id(client, business_id)

        ad_accounts = await client.get(
            f"/{bid}/owned_ad_accounts",
            {"fields": "id,account_id,name,currency,account_status"},
            paginate=True,
        )
        pages = await client.get(
            f"/{bid}/owned_pages",
            {"fields": "id,name,category"},
            paginate=True,
        )
        instagram = await client.get(
            f"/{bid}/owned_instagram_accounts",
            {"fields": "id,username"},
            paginate=True,
        )
        system_users = await client.get(
            f"/{bid}/system_users",
            {"fields": "id,name,role"},
            paginate=True,
        )
        return {
            "business_id": bid,
            "ad_accounts": ad_accounts.get("data", []),
            "pages": pages.get("data", []),
            "instagram_accounts": instagram.get("data", []),
            "system_users": system_users.get("data", []),
        }

    @mcp.tool()
    async def list_owned_ad_accounts(business_id: str | None = None) -> dict[str, Any]:
        """List ad accounts owned by the Meta Business (not just user-assigned)."""
        client: MetaClient = get_client()
        bid = _resolve_business_id(client, business_id)
        return await client.get(
            f"/{bid}/owned_ad_accounts",
            {"fields": "id,account_id,name,currency,account_status,timezone_name"},
            paginate=True,
        )

    @mcp.tool()
    async def list_owned_pages(business_id: str | None = None) -> dict[str, Any]:
        """List Pages owned by the Meta Business."""
        client: MetaClient = get_client()
        bid = _resolve_business_id(client, business_id)
        return await client.get(
            f"/{bid}/owned_pages",
            {"fields": "id,name,category,link"},
            paginate=True,
        )

    @mcp.tool()
    async def list_client_ad_accounts(business_id: str | None = None) -> dict[str, Any]:
        """List ad accounts shared WITH this business by clients or partners.

        Useful for agencies: these are accounts you can manage but don't own.
        """
        client: MetaClient = get_client()
        bid = _resolve_business_id(client, business_id)
        return await client.get(
            f"/{bid}/client_ad_accounts",
            {"fields": "id,account_id,name,currency,account_status"},
            paginate=True,
        )

    @mcp.tool()
    async def list_business_system_users(business_id: str | None = None) -> dict[str, Any]:
        """List System Users under the Meta Business (admin view)."""
        client: MetaClient = get_client()
        bid = _resolve_business_id(client, business_id)
        return await client.get(
            f"/{bid}/system_users",
            {"fields": "id,name,role"},
            paginate=True,
        )
