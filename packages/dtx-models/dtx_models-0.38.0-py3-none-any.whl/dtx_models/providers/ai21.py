from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class AI21ProviderConfig(BaseProviderConfig):
    type: Literal["ai21"] = Field("ai21", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for AI21 API (AI21_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for AI21 (AI21_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class AI21Provider(BaseModel):
    provider: Literal["ai21"] = Field("ai21", description="Provider ID for AI21.")
    config: AI21ProviderConfig
