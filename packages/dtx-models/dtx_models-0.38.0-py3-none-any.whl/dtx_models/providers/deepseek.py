from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class DeepseekProviderConfig(BaseProviderConfig):
    type: Literal["deepseek"] = Field("deepseek", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Deepseek API (DEEPSEEK_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Deepseek (DEEPSEEK_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class DeepseekProvider(BaseModel):
    provider: Literal["deepseek"] = Field("deepseek", description="Provider ID for Deepseek.")
    config: DeepseekProviderConfig
