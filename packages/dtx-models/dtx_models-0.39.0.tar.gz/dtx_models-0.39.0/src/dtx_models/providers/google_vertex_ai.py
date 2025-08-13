from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class VertexAIProviderConfig(BaseProviderConfig):
    type: Literal["vertexai"] = Field("vertexai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the Vertex AI endpoint (VERTEXAI_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Vertex AI (VERTEXAI_API_KEY)."
    )
    project: Optional[str] = Field(
        default=None,
        description="GCP Project ID for Vertex AI (VERTEXAI_PROJECT)."
    )
    location: Optional[str] = Field(
        default=None,
        description="GCP Region/Location for Vertex AI (VERTEXAI_LOCATION)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Vertex AI (VERTEXAI_API_VERSION)."
    )
    service_account_json: Optional[str] = Field(
        default=None,
        description="Optional path or JSON string for service account auth (VERTEXAI_SERVICE_ACCOUNT_JSON)."
    )

    def get_name(self) -> str:
        return self.model

class VertexAIProvider(BaseModel):
    provider: Literal["vertexai"] = Field("vertexai", description="Provider ID for Google Vertex AI.")
    config: VertexAIProviderConfig
