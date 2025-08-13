from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class AzureAIProviderConfig(BaseProviderConfig):
    type: Literal["azure_ai"] = Field("azure_ai", description="Provider type discriminator.")
    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the Azure AI Studio endpoint (AZURE_AI_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Azure AI Studio (AZURE_AI_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional): override default version."
    )

    def get_name(self) -> str:
        return self.model

class AzureAIProvider(BaseModel):
    provider: Literal["azure_ai"] = Field("azure_ai", description="Provider ID for Azure AI Studio.")
    config: AzureAIProviderConfig
