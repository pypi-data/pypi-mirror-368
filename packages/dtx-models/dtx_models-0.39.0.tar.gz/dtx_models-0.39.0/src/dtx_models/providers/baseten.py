from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class BasetenProviderConfig(BaseProviderConfig):
    type: Literal["baseten"] = Field("baseten", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Baseten API (BASETEN_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Baseten (BASETEN_API_KEY)."
    )
    model_id: Optional[str] = Field(
        default=None,
        description="Baseten deployed model ID (BASETEN_MODEL_ID)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Baseten (BASETEN_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class BasetenProvider(BaseModel):
    provider: Literal["baseten"] = Field("baseten", description="Provider ID for Baseten.")
    config: BasetenProviderConfig
