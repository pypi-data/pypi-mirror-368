from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class FeatherlessAIProviderConfig(BaseProviderConfig):
    type: Literal["featherless_ai"] = Field("featherless_ai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for the Featherless AI API (FEATHERLESS_AI_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Featherless AI (FEATHERLESS_AI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Featherless AI (FEATHERLESS_AI_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class FeatherlessAIProvider(BaseModel):
    provider: Literal["featherless_ai"] = Field("featherless_ai", description="Provider ID for Featherless AI.")
    config: FeatherlessAIProviderConfig
