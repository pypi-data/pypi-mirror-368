from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class TritonProviderConfig(BaseProviderConfig):
    type: Literal["triton"] = Field("triton", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for the Triton Inference Server (TRITON_API_BASE)."
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Name of the deployed model in Triton."
    )
    model_version: Optional[str] = Field(
        default=None,
        description="Version of the deployed model in Triton."
    )

    def get_name(self) -> str:
        return self.model

class TritonProvider(BaseModel):
    provider: Literal["triton"] = Field("triton", description="Provider ID for Triton Inference Server.")
    config: TritonProviderConfig
