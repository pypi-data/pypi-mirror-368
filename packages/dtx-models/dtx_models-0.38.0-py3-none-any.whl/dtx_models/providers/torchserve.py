from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class TorchServeProviderConfig(BaseProviderConfig):
    type: Literal["torchserve"] = Field("torchserve", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for the TorchServe API server (TORCHSERVE_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for TorchServe if required (TORCHSERVE_API_KEY)."
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Name of the model deployed on TorchServe."
    )
    model_version: Optional[str] = Field(
        default=None,
        description="Model version on TorchServe."
    )

    def get_name(self) -> str:
        return self.model

class TorchServeProvider(BaseModel):
    provider: Literal["torchserve"] = Field("torchserve", description="Provider ID for TorchServe API Server.")
    config: TorchServeProviderConfig
