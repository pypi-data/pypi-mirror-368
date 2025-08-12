from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class TopazProviderConfig(BaseProviderConfig):
    type: Literal["topaz"] = Field("topaz", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Topaz API (TOPAZ_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Topaz (TOPAZ_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class TopazProvider(BaseModel):
    provider: Literal["topaz"] = Field("topaz", description="Provider ID for Topaz.")
    config: TopazProviderConfig
