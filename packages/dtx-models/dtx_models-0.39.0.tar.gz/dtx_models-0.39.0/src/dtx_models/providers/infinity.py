from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class InfinityProviderConfig(BaseProviderConfig):
    type: Literal["infinity"] = Field("infinity", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the Infinity endpoint (INFINITY_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Infinity (INFINITY_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Infinity (INFINITY_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class InfinityProvider(BaseModel):
    provider: Literal["infinity"] = Field("infinity", description="Provider ID for Infinity.")
    config: InfinityProviderConfig
