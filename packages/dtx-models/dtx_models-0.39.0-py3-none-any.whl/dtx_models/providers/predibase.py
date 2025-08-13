from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class PredibaseProviderConfig(BaseProviderConfig):
    type: Literal["predibase"] = Field("predibase", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Predibase API (PREDIBASE_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Predibase (PREDIBASE_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class PredibaseProvider(BaseModel):
    provider: Literal["predibase"] = Field("predibase", description="Provider ID for Predibase.")
    config: PredibaseProviderConfig
