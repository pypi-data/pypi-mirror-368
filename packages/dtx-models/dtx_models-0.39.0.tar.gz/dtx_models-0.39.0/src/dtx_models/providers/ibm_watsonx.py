from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class IBMWatsonxProviderConfig(BaseProviderConfig):
    type: Literal["ibm_watsonx"] = Field("ibm_watsonx", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for IBM watsonx.ai API (IBM_WATSONX_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for IBM watsonx.ai (IBM_WATSONX_API_KEY)."
    )
    instance_id: Optional[str] = Field(
        default=None,
        description="IBM Cloud instance ID for watsonx.ai (IBM_WATSONX_INSTANCE_ID)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v2')."
    )

    def get_name(self) -> str:
        return self.model

class IBMWatsonxProvider(BaseModel):
    provider: Literal["ibm_watsonx"] = Field("ibm_watsonx", description="Provider ID for IBM watsonx.ai.")
    config: IBMWatsonxProviderConfig
