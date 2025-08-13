from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class GeminiProviderConfig(BaseProviderConfig):
    type: Literal["gemini"] = Field("gemini", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Gemini API (GEMINI_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Gemini (GEMINI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )
    env_vars: Dict[str, str] = {
        "GEMINI_API_KEY": "api_key",
        "GEMINI_API_BASE": "endpoint",
    }

    def get_name(self) -> str:
        return self.model

class GeminiProvider(BaseModel):
    provider: Literal["gemini"] = Field("gemini", description="Provider ID for Gemini.")
    config: GeminiProviderConfig
