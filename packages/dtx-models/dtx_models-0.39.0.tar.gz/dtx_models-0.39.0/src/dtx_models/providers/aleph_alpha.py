from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class AlephAlphaProviderConfig(BaseProviderConfig):
    type: Literal["aleph_alpha"] = Field("aleph_alpha", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Aleph Alpha API (ALEPH_ALPHA_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Aleph Alpha (ALEPH_ALPHA_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Aleph Alpha (ALEPH_ALPHA_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class AlephAlphaProvider(BaseModel):
    provider: Literal["aleph_alpha"] = Field("aleph_alpha", description="Provider ID for Aleph Alpha.")
    config: AlephAlphaProviderConfig
