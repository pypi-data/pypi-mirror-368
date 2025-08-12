from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class VolcengineProviderConfig(BaseProviderConfig):
    type: Literal["volcengine"] = Field("volcengine", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Volcengine API (VOLCENGINE_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Volcengine (VOLCENGINE_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class VolcengineProvider(BaseModel):
    provider: Literal["volcengine"] = Field("volcengine", description="Provider ID for Volcengine.")
    config: VolcengineProviderConfig
