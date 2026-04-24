from typing import Any

from mcp.server.fastmcp import FastMCP

from meta_insights_mcp.meta_client import MetaClient

DEFAULT_PAGE_METRICS = [
    "page_impressions",
    "page_post_engagements",
    "page_fans",
]

DEFAULT_POST_METRICS = [
    "post_impressions",
    "post_engaged_users",
    "post_clicks",
]


def register(mcp: FastMCP, get_client) -> None:
    @mcp.tool()
    async def get_page_insights(
        page_id: str,
        metrics: list[str] | None = None,
        period: str = "day",
    ) -> dict[str, Any]:
        """Fetch organic Page insights.

        Args:
            page_id: Facebook Page ID.
            metrics: Page insight metric names. Defaults to impressions,
                post engagements, and fans.
            period: `day`, `week`, `days_28`, or `lifetime`.
        """
        client: MetaClient = get_client()
        params = {
            "metric": ",".join(metrics or DEFAULT_PAGE_METRICS),
            "period": period,
        }
        return await client.get(f"/{page_id}/insights", params, paginate=True)

    @mcp.tool()
    async def get_post_insights(
        post_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Fetch insights for a single Page post.

        Args:
            post_id: Page post ID (format: `{page_id}_{post_id}`).
            metrics: Post insight metric names. Defaults to impressions,
                engaged users, and clicks.
        """
        client: MetaClient = get_client()
        params = {"metric": ",".join(metrics or DEFAULT_POST_METRICS)}
        return await client.get(f"/{post_id}/insights", params)

    @mcp.tool()
    async def list_page_posts(
        page_id: str,
        limit: int = 25,
    ) -> dict[str, Any]:
        """List recent posts from a Page.

        Args:
            page_id: Facebook Page ID.
            limit: Number of posts per request (max 100).
        """
        client: MetaClient = get_client()
        params = {
            "fields": "id,message,created_time,permalink_url",
            "limit": min(max(limit, 1), 100),
        }
        return await client.get(f"/{page_id}/posts", params, paginate=True)
