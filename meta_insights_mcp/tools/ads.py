from typing import Any

from mcp.server.fastmcp import FastMCP

from meta_insights_mcp.meta_client import MetaClient

DEFAULT_AD_FIELDS = [
    "campaign_name",
    "adset_name",
    "ad_name",
    "impressions",
    "reach",
    "clicks",
    "spend",
    "ctr",
    "cpc",
    "cpm",
    "actions",
]


def _normalize_ad_account_id(ad_account_id: str) -> str:
    aid = ad_account_id.strip()
    return aid if aid.startswith("act_") else f"act_{aid}"


def register(mcp: FastMCP, get_client) -> None:
    @mcp.tool()
    async def get_ad_account_insights(
        ad_account_id: str,
        fields: list[str] | None = None,
        date_preset: str = "last_30d",
        level: str = "ad",
    ) -> dict[str, Any]:
        """Fetch ads performance insights for an ad account.

        Args:
            ad_account_id: Ad account ID, with or without the `act_` prefix.
            fields: Insight fields to request. Defaults to a common set
                (campaign_name, ad_name, impressions, clicks, spend, ctr, cpc, ...).
            date_preset: Meta preset such as `today`, `yesterday`, `last_7d`,
                `last_30d`, `this_month`, `last_month`, `maximum`.
            level: Granularity — `account`, `campaign`, `adset`, or `ad`.

        Returns the Meta `data` array plus pagination info.
        """
        client: MetaClient = get_client()
        aid = _normalize_ad_account_id(ad_account_id)
        params = {
            "fields": ",".join(fields or DEFAULT_AD_FIELDS),
            "date_preset": date_preset,
            "level": level,
        }
        return await client.get(f"/{aid}/insights", params, paginate=True)

    @mcp.tool()
    async def get_campaign_insights(
        campaign_id: str,
        fields: list[str] | None = None,
        date_preset: str = "last_30d",
    ) -> dict[str, Any]:
        """Fetch insights for a single campaign by ID.

        Args:
            campaign_id: Meta campaign ID.
            fields: Insight fields. Defaults to common performance fields.
            date_preset: e.g. `last_7d`, `last_30d`, `maximum`.
        """
        client: MetaClient = get_client()
        params = {
            "fields": ",".join(fields or DEFAULT_AD_FIELDS),
            "date_preset": date_preset,
        }
        return await client.get(f"/{campaign_id}/insights", params, paginate=True)

    @mcp.tool()
    async def list_campaigns(
        ad_account_id: str,
        effective_status: list[str] | None = None,
    ) -> dict[str, Any]:
        """List campaigns under an ad account.

        Args:
            ad_account_id: Ad account ID, with or without the `act_` prefix.
            effective_status: Optional filter, e.g. `["ACTIVE", "PAUSED"]`.
        """
        client: MetaClient = get_client()
        aid = _normalize_ad_account_id(ad_account_id)
        params: dict[str, Any] = {
            "fields": "id,name,objective,status,effective_status,daily_budget,lifetime_budget",
        }
        if effective_status:
            params["effective_status"] = str(effective_status).replace("'", '"')
        return await client.get(f"/{aid}/campaigns", params, paginate=True)
