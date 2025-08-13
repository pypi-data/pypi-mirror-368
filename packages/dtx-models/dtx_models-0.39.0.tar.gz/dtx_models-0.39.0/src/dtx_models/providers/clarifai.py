from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class ClarifaiProviderConfig(BaseProviderConfig):
    type: Literal["clarifai"] = Field("clarifai", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Clarifai API (CLARIFAI_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Clarifai (CLARIFAI_API_KEY)."
    )
    app_id: Optional[str] = Field(
        default=None,
        description="Clarifai App ID (CLARIFAI_APP_ID, optional)."
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Clarifai User ID (CLARIFAI_USER_ID, optional)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v2')."
    )

    def get_name(self) -> str:
        return self.model

class ClarifaiProvider(BaseModel):
    provider: Literal["clarifai"] = Field("clarifai", description="Provider ID for Clarifai.")
    config: ClarifaiProviderConfig
