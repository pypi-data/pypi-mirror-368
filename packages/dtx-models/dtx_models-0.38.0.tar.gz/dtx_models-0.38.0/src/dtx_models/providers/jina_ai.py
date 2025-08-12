from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class JinaAIProviderConfig(BaseProviderConfig):
    type: Literal["jina_ai"] = Field("jina_ai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Jina AI API (JINA_AI_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Jina AI (JINA_AI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Jina AI (JINA_AI_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class JinaAIProvider(BaseModel):
    provider: Literal["jina_ai"] = Field("jina_ai", description="Provider ID for Jina AI.")
    config: JinaAIProviderConfig
