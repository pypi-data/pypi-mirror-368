from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class VLLMProviderConfig(BaseProviderConfig):
    type: Literal["vllm"] = Field("vllm", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for VLLM API (VLLM_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for VLLM (VLLM_API_KEY, optional if required)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class VLLMProvider(BaseModel):
    provider: Literal["vllm"] = Field("vllm", description="Provider ID for VLLM.")
    config: VLLMProviderConfig
