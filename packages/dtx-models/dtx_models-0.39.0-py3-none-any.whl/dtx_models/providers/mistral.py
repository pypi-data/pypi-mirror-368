from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class MistralProviderConfig(BaseProviderConfig):
    type: Literal["mistral"] = Field("mistral", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Mistral API (MISTRAL_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Mistral (MISTRAL_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., v1)."
    )
    env_vars: Dict[str, str] = {
        "MISTRAL_API_KEY": "api_key",
        "MISTRAL_API_BASE": "endpoint",
    }

    def get_name(self) -> str:
        return self.model

class MistralProvider(BaseModel):
    provider: Literal["mistral"] = Field("mistral", description="Provider ID for Mistral AI.")
    config: MistralProviderConfig
