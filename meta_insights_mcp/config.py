import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    access_token: str
    api_version: str
    business_id: str | None
    base_url: str

    @property
    def graph_url(self) -> str:
        return f"{self.base_url}/{self.api_version}"


def load_settings() -> Settings:
    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    if not token or token == "replace_me":
        raise RuntimeError(
            "META_ACCESS_TOKEN is not set. Add it to .env before starting the server."
        )
    return Settings(
        access_token=token,
        api_version=os.getenv("META_API_VERSION", "v23.0"),
        business_id=os.getenv("META_BUSINESS_ID") or None,
        base_url="https://graph.facebook.com",
    )
