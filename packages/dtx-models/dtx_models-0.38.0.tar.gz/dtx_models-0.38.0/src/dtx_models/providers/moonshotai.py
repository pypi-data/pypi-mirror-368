from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class MoonshotAIProviderConfig(BaseProviderConfig):
    type: Literal["moonshotai"] = Field("moonshotai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Moonshot AI API (MOONSHOTAI_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Moonshot AI (MOONSHOTAI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class MoonshotAIProvider(BaseModel):
    provider: Literal["moonshotai"] = Field("moonshotai", description="Provider ID for Moonshot AI.")
    config: MoonshotAIProviderConfig
