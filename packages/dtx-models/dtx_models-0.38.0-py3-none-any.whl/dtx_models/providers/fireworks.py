from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class FireworksProviderConfig(BaseProviderConfig):
    type: Literal["fireworks"] = Field("fireworks", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Fireworks AI API (FIREWORKS_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Fireworks AI (FIREWORKS_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class FireworksProvider(BaseModel):
    provider: Literal["fireworks"] = Field("fireworks", description="Provider ID for Fireworks AI.")
    config: FireworksProviderConfig
