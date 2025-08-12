from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig
from dtx_models.providers.models_spec import ModelTaskType

class DeepgramProviderConfig(BaseProviderConfig):
    type: Literal["deepgram"] = Field("deepgram", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Deepgram API (DEEPGRAM_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Deepgram (DEEPGRAM_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )
    model: str = Field(
        ...,
        description="Deepgram STT model (e.g. 'nova-2', 'whisper-large')."
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code for transcription (optional, e.g., 'en')."
    )
    task: ModelTaskType = Field(
        default=ModelTaskType.TRANSCRIPTION,
        description="Task type for Deepgram (always 'transcription')."
    )

    def get_name(self) -> str:
        return self.model

class DeepgramProvider(BaseModel):
    provider: Literal["deepgram"] = Field("deepgram", description="Provider ID for Deepgram STT.")
    config: DeepgramProviderConfig
