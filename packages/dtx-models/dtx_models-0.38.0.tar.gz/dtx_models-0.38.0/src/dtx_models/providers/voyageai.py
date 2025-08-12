from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class VoyageAIProviderConfig(BaseProviderConfig):
    type: Literal["voyageai"] = Field("voyageai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Voyage AI API (VOYAGEAI_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Voyage AI (VOYAGEAI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class VoyageAIProvider(BaseModel):
    provider: Literal["voyageai"] = Field("voyageai", description="Provider ID for Voyage AI.")
    config: VoyageAIProviderConfig
