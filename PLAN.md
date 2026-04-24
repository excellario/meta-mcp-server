# Meta Insights MCP Server — Build Plan

## Goal
Expose Meta (Facebook/Instagram) business insights to an AI platform via an MCP server, using a pre-generated System User access token.

## Stack
- **Python 3.11+**
- **`mcp[cli]`** — official MCP Python SDK (FastMCP)
- **`httpx`** — async HTTP client for Graph API
- **`pydantic`** — tool input/output schemas
- **`python-dotenv`** — local env loading
- **`venv`** — environment management

## Project layout
```
meta-mcp-server/
├── .env / .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── PLAN.md
└── src/
    ├── __init__.py
    ├── server.py          # FastMCP entry point
    ├── config.py          # env + constants
    ├── meta_client.py     # httpx wrapper around Graph API
    └── tools/
        ├── __init__.py
        ├── assets.py      # list assets, token status
        ├── ads.py         # ad account / campaign insights
        └── pages.py       # page / post insights
```

## Checklist

### 1. Project setup
- [ ] Create `venv`
- [ ] Create `.gitignore`, `.env.example`, `.env`
- [ ] Write `requirements.txt`
- [ ] Install dependencies

### 2. Core client (`meta_client.py`)
- [ ] Single `httpx.AsyncClient` with base URL `https://graph.facebook.com/{version}`
- [ ] Inject access token automatically
- [ ] Parse Meta error JSON → raise typed errors
- [ ] Retry with exponential backoff on 429/5xx
- [ ] Auto-paginate cursor responses

### 3. MCP tools
- [ ] `list_meta_assets()`
- [ ] `check_token_status()`
- [ ] `get_ad_account_insights(ad_account_id, fields?, date_preset?, level?)`
- [ ] `get_campaign_insights(campaign_id, fields?, date_preset?)`
- [ ] `get_page_insights(page_id, metrics, period?)`
- [ ] `get_post_insights(post_id, metrics)`

### 4. Best practices
- Typed Pydantic inputs → auto JSON schema
- Docstrings on every tool (model reads them)
- Stdio transport by default
- Never log the token; mask in error messages
- Validate inputs before calling Meta
- Return normalized dicts, not raw payloads

### 5. Run & test
- [ ] Smoke test with `mcp dev` inspector
- [ ] Document Claude Desktop / Claude Code registration

### 6. Later (out of scope for v1)
- Webhook receiver (separate FastAPI process)
- Caching layer (5-min TTL)
- HTTP/SSE transport for remote hosting
