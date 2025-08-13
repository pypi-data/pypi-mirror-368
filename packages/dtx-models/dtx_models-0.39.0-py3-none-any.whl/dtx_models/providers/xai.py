from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class XAIProviderConfig(BaseProviderConfig):
    type: Literal["xai"] = Field("xai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for xAI Grok API (XAI_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for xAI Grok (XAI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class XAIProvider(BaseModel):
    provider: Literal["xai"] = Field("xai", description="Provider ID for xAI (Grok).")
    config: XAIProviderConfig
