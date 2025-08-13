from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class GaladrielProviderConfig(BaseProviderConfig):
    type: Literal["galadriel"] = Field("galadriel", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Galadriel API (GALADRIEL_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Galadriel (GALADRIEL_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Galadriel (GALADRIEL_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class GaladrielProvider(BaseModel):
    provider: Literal["galadriel"] = Field("galadriel", description="Provider ID for Galadriel.")
    config: GaladrielProviderConfig
