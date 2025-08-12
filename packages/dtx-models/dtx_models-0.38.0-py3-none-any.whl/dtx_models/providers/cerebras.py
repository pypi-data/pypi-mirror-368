from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class CerebrasProviderConfig(BaseProviderConfig):
    type: Literal["cerebras"] = Field("cerebras", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Cerebras API (CEREBRAS_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Cerebras (CEREBRAS_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v2')."
    )
    env_vars: Dict[str, str] = {
        "CEREBRAS_API_KEY": "api_key",
        "CEREBRAS_API_BASE": "endpoint",
    }

    def get_name(self) -> str:
        return self.model

class CerebrasProvider(BaseModel):
    provider: Literal["cerebras"] = Field("cerebras", description="Provider ID for Cerebras.")
    config: CerebrasProviderConfig
