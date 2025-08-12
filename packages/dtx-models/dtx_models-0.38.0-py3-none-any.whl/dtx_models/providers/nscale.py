from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class NscaleProviderConfig(BaseProviderConfig):
    type: Literal["nscale"] = Field("nscale", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Nscale API (NSCALE_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Nscale (NSCALE_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Nscale (NSCALE_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class NscaleProvider(BaseModel):
    provider: Literal["nscale"] = Field("nscale", description="Provider ID for Nscale.")
    config: NscaleProviderConfig
