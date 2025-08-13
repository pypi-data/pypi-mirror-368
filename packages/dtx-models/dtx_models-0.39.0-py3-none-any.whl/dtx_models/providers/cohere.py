from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class CohereProviderConfig(BaseProviderConfig):
    type: Literal["cohere"] = Field("cohere", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Cohere API (COHERE_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Cohere (COHERE_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., '2022-12-06')."
    )

    def get_name(self) -> str:
        return self.model

class CohereProvider(BaseModel):
    provider: Literal["cohere"] = Field("cohere", description="Provider ID for Cohere.")
    config: CohereProviderConfig
    