from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class TogetherProviderConfig(BaseProviderConfig):
    type: Literal["together"] = Field("together", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Together AI API (TOGETHER_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Together AI (TOGETHER_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class TogetherProvider(BaseModel):
    provider: Literal["together"] = Field("together", description="Provider ID for Together AI.")
    config: TogetherProviderConfig
