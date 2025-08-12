from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class LMStudioProviderConfig(BaseProviderConfig):
    type: Literal["lmstudio"] = Field("lmstudio", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for LM Studio API (LMSTUDIO_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for LM Studio (LMSTUDIO_API_KEY, optional if not required)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class LMStudioProvider(BaseModel):
    provider: Literal["lmstudio"] = Field("lmstudio", description="Provider ID for LM Studio.")
    config: LMStudioProviderConfig
