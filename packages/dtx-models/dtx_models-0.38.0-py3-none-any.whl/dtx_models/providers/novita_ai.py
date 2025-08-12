from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class NovitaAIProviderConfig(BaseProviderConfig):
    type: Literal["novita_ai"] = Field("novita_ai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Novita AI API (NOVITA_AI_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Novita AI (NOVITA_AI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Novita AI (NOVITA_AI_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class NovitaAIProvider(BaseModel):
    provider: Literal["novita_ai"] = Field("novita_ai", description="Provider ID for Novita AI.")
    config: NovitaAIProviderConfig
