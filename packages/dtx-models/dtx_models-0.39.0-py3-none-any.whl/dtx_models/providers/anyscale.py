from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class AnyscaleProviderConfig(BaseProviderConfig):
    type: Literal["anyscale"] = Field("anyscale", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Anyscale API (ANYSCALE_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Anyscale (ANYSCALE_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class AnyscaleProvider(BaseModel):
    provider: Literal["anyscale"] = Field("anyscale", description="Provider ID for Anyscale.")
    config: AnyscaleProviderConfig
