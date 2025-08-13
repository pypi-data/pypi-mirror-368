from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class PerplexityProviderConfig(BaseProviderConfig):
    type: Literal["perplexity"] = Field("perplexity", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Perplexity pplx-api (PERPLEXITY_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Perplexity (PERPLEXITY_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class PerplexityProvider(BaseModel):
    provider: Literal["perplexity"] = Field("perplexity", description="Provider ID for Perplexity (pplx-api).")
    config: PerplexityProviderConfig
