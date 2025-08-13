from typing import Literal, Optional
from pydantic import BaseModel, Field

from .openai import BaseProviderConfig

class MetaLlamaProviderConfig(BaseProviderConfig):
    type: Literal["meta_llama"] = Field("meta_llama", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Meta Llama API (META_LLAMA_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Meta Llama (META_LLAMA_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )

    def get_name(self) -> str:
        return self.model

class MetaLlamaProvider(BaseModel):
    provider: Literal["meta_llama"] = Field("meta_llama", description="Provider ID for Meta Llama.")
    config: MetaLlamaProviderConfig
