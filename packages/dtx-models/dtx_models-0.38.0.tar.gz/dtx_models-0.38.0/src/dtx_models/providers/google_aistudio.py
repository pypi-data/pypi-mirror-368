from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class GoogleAIStudioProviderConfig(BaseProviderConfig):
    type: Literal["google_aistudio"] = Field("google_aistudio", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Google AI Studio API (GOOGLE_AISTUDIO_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Google AI Studio (GOOGLE_AISTUDIO_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class GoogleAIStudioProvider(BaseModel):
    provider: Literal["google_aistudio"] = Field("google_aistudio", description="Provider ID for Google AI Studio.")
    config: GoogleAIStudioProviderConfig
