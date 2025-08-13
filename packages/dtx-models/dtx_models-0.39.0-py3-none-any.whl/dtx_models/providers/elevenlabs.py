from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig
from dtx_models.providers.models_spec import ModelTaskType

class ElevenLabsProviderConfig(BaseProviderConfig):
    type: Literal["elevenlabs"] = Field("elevenlabs", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for ElevenLabs API (ELEVENLABS_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for ElevenLabs (ELEVENLABS_API_KEY)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., 'v1')."
    )
    voice_id: Optional[str] = Field(
        default=None,
        description="Voice ID for TTS (ELEVENLABS_VOICE_ID, optional for TTS)."
    )
    model: str = Field(
        ...,
        description="Model name for ElevenLabs (e.g., 'eleven_multilingual_v2', 'speech-to-text', etc)."
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code (optional, e.g., 'en', for TTS or STT)."
    )
    task: ModelTaskType = Field(
        default=ModelTaskType.TEXT_TO_SPEECH,
        description="Task type for ElevenLabs: TTS or STT. Override for STT as needed."
    )

    def get_name(self) -> str:
        return self.model

class ElevenLabsProvider(BaseModel):
    provider: Literal["elevenlabs"] = Field("elevenlabs", description="Provider ID for ElevenLabs TTS/STT.")
    config: ElevenLabsProviderConfig
