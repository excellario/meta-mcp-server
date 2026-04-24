# meta-insights-mcp

An MCP server exposing Meta (Facebook / Instagram) business insights through the Graph and Marketing APIs, using a System User access token.

## Install

```bash
pip install meta-insights-mcp
# or
uv add meta-insights-mcp
# or run ad-hoc without installing
uvx meta-insights-mcp
```

## Configuration

The server reads its configuration from environment variables:

| Var | Required | Default | Purpose |
|-----|----------|---------|---------|
| `META_ACCESS_TOKEN` | **yes** | — | System User access token |
| `META_API_VERSION` | no | `v23.0` | Graph API version |
| `META_BUSINESS_ID` | no | — | When set, enables business-scoped tools (`list_business_assets`, etc.) |

## Connect to Claude

Add one of the following to your MCP client config (Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json`; Claude Code: `~/.claude.json` or project `.mcp.json`).

### Recommended — zero-install via `uvx`

```json
{
  "mcpServers": {
    "meta-insights": {
      "command": "uvx",
      "args": ["meta-insights-mcp"],
      "env": {
        "META_ACCESS_TOKEN": "EAAG..."
      }
    }
  }
}
```

### After `pip install`

```json
{
  "mcpServers": {
    "meta-insights": {
      "command": "meta-insights-mcp",
      "env": {
        "META_ACCESS_TOKEN": "EAAG..."
      }
    }
  }
}
```

### Module form (fallback)

```json
{
  "mcpServers": {
    "meta-insights": {
      "command": "python",
      "args": ["-m", "meta_insights_mcp"],
      "env": {
        "META_ACCESS_TOKEN": "EAAG..."
      }
    }
  }
}
```

## Tools

### User-scoped (always available)

| Tool | Purpose |
|------|---------|
| `list_meta_assets` | Ad accounts + Pages the token can see |
| `check_token_status` | Token scopes, app, expiry |
| `get_ad_account_insights` | Ads performance for an ad account |
| `get_campaign_insights` | Insights for a single campaign |
| `list_campaigns` | List campaigns under an ad account |
| `get_page_insights` | Organic Page insights |
| `get_post_insights` | Insights for a single Page post |
| `list_page_posts` | Recent posts from a Page |

### Business-scoped (enabled when `META_BUSINESS_ID` is set)

| Tool | Purpose |
|------|---------|
| `list_business_assets` | Everything the business owns (ad accounts, Pages, IG, System Users) |
| `list_owned_ad_accounts` | Ad accounts owned by the business |
| `list_owned_pages` | Pages owned by the business |
| `list_client_ad_accounts` | Ad accounts shared WITH this business by clients/partners |
| `list_business_system_users` | System Users under the business |

## Meta setup required

Before the server returns data, you need (in Meta Business Manager):

1. A **Business App** in Meta for Developers tied to your Business Manager
2. A **System User** with scopes: `ads_read` or `ads_management`, `pages_read_engagement`, `business_management`
3. **Asset assignment**: assign the Ad Account(s) and Page(s) you want to read to the System User (this is the step people most often miss — a valid token with unassigned assets returns empty data)
4. A **System User access token** — pass it as `META_ACCESS_TOKEN`

Use `check_token_status` to verify scopes and expiry.

## Testing locally with the MCP Inspector

The MCP Inspector is a browser-based UI (provided by Anthropic) that lets you call your tools directly — no AI needed. Great for verifying the server works before connecting it to Claude.

```bash
# From the project root, with your venv active
mcp dev meta_insights_mcp/server.py
```

This launches:
- Your Python MCP server
- A local web UI (opens automatically in your browser)

**In the Inspector:**

1. Click **Connect** at the top
2. Open the **Tools** tab
3. Try these in order:
   - **`check_token_status`** — no args; confirms your token is valid and shows scopes/expiry
   - **`list_meta_assets`** — no args; lists ad accounts and Pages assigned to the System User
   - **`get_ad_account_insights`** — paste an `ad_account_id` from the previous step
4. Enable business-scoped tools by setting `META_BUSINESS_ID` in your shell / `.env` before launching the Inspector, then call **`list_business_assets`**

If `list_meta_assets` returns empty arrays, the token is fine but the System User has no assets assigned yet — fix that in Meta Business Settings (see "Meta setup required" above).

## Development

```bash
git clone <repo>
cd meta-mcp-server
python3 -m venv .venv && source .venv/bin/activate
pip install -e .        # editable install

# Run the MCP Inspector
mcp dev meta_insights_mcp/server.py

# Or run the server directly (stdio)
meta-insights-mcp
```

## Publishing

Build wheel + sdist:

```bash
pip install build
python -m build        # produces dist/*.whl and dist/*.tar.gz
```

Upload to TestPyPI first (sandbox):

```bash
pip install twine
python -m twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple/ meta-insights-mcp   # verify
```

Then to real PyPI:

```bash
python -m twine upload dist/*
```

## License

MIT
