from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class SambaNovaProviderConfig(BaseProviderConfig):
    type: Literal["sambanova"] = Field("sambanova", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for SambaNova API (SAMBANOVA_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for SambaNova (SAMBANOVA_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for SambaNova (SAMBANOVA_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class SambaNovaProvider(BaseModel):
    provider: Literal["sambanova"] = Field("sambanova", description="Provider ID for SambaNova.")
    config: SambaNovaProviderConfig
