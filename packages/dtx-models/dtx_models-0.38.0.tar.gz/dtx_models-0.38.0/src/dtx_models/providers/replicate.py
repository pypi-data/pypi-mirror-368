from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class ReplicateProviderConfig(BaseProviderConfig):
    type: Literal["replicate"] = Field("replicate", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Replicate API (REPLICATE_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Replicate (REPLICATE_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class ReplicateProvider(BaseModel):
    provider: Literal["replicate"] = Field("replicate", description="Provider ID for Replicate.")
    config: ReplicateProviderConfig
