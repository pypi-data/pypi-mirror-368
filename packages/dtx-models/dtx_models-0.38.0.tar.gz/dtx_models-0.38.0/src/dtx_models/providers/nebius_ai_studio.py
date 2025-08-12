from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class NebiusAIStudioProviderConfig(BaseProviderConfig):
    type: Literal["nebius_ai_studio"] = Field("nebius_ai_studio", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the Nebius AI Studio endpoint (NEBIUS_AI_STUDIO_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Nebius AI Studio (NEBIUS_AI_STUDIO_API_KEY)."
    )
    folder_id: Optional[str] = Field(
        default=None,
        description="Folder ID for Nebius AI Studio (NEBIUS_AI_STUDIO_FOLDER_ID)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Nebius AI Studio (NEBIUS_AI_STUDIO_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class NebiusAIStudioProvider(BaseModel):
    provider: Literal["nebius_ai_studio"] = Field("nebius_ai_studio", description="Provider ID for Nebius AI Studio.")
    config: NebiusAIStudioProviderConfig
