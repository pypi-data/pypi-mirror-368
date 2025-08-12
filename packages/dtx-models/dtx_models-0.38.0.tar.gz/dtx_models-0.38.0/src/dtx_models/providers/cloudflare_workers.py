from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class CloudflareWorkersProviderConfig(BaseProviderConfig):
    type: Literal["cloudflare_workers"] = Field("cloudflare_workers", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Cloudflare Workers AI API (CLOUDFLARE_WORKERS_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Cloudflare Workers AI (CLOUDFLARE_WORKERS_API_KEY)."
    )
    account_id: Optional[str] = Field(
        default=None,
        description="Cloudflare account ID (CLOUDFLARE_WORKERS_ACCOUNT_ID, optional)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class CloudflareWorkersProvider(BaseModel):
    provider: Literal["cloudflare_workers"] = Field("cloudflare_workers", description="Provider ID for Cloudflare Workers AI.")
    config: CloudflareWorkersProviderConfig
