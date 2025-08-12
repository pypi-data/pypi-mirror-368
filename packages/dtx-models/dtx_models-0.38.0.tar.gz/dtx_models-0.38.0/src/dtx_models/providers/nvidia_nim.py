from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class NvidiaNIMProviderConfig(BaseProviderConfig):
    type: Literal["nvidia_nim"] = Field("nvidia_nim", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Nvidia NIM API (NVIDIA_NIM_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Nvidia NIM (NVIDIA_NIM_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class NvidiaNIMProvider(BaseModel):
    provider: Literal["nvidia_nim"] = Field("nvidia_nim", description="Provider ID for Nvidia NIM.")
    config: NvidiaNIMProviderConfig
