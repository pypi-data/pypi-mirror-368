from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class AzureProviderConfig(BaseProviderConfig):
    type: Literal["azure"] = Field("azure", description="Provider type discriminator.")
    
    # Base endpoint, typically your Azure OpenAI resource URL
    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the Azure OpenAI resource (AZURE_API_BASE or provided explicitly)."
    )

    api_version: Optional[str] = Field(
        default=None,
        description="API version for Azure OpenAI (e.g. '2023-05-15-preview')."
    )

    azure_ad_token: Optional[str] = Field(
        default=None,
        description="Optional Azure AD access token for managed identity (AZURE_AD_TOKEN)."
    )
    env_vars: Dict[str, str] = {
        "Azure_API_KEY": "api_key",
        "Azure_API_BASE": "endpoint",
    }

    def get_name(self) -> str:
        return self.model

class AzureProvider(BaseModel):
    provider: Literal["azure"] = Field("azure", description="Provider ID for Azure OpenAI.")
    config: AzureProviderConfig