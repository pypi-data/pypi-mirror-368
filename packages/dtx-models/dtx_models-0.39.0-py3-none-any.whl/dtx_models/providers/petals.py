from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class PetalsProviderConfig(BaseProviderConfig):
    type: Literal["petals"] = Field("petals", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Petals API (PETALS_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Petals (PETALS_API_KEY, optional if required)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class PetalsProvider(BaseModel):
    provider: Literal["petals"] = Field("petals", description="Provider ID for Petals.")
    config: PetalsProviderConfig
