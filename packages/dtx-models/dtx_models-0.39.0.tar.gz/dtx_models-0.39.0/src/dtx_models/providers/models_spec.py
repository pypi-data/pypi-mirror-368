from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from ..providers.base import ProviderType

# --- Define Modalities ---

class Modality(str, Enum):
    """
    Represents the input/output modality a model supports.
    """
    TEXT = "text"
    IMAGE = "image"
    CODE = "code"
    AUDIO = "audio"
    VIDEO = "video"
    VISION = "vision"         # General-purpose image/video analysis
    DOCUMENT = "document"     # Multi-page hybrid formats (e.g., PDFs)
    TABULAR = "tabular"       # Structured data like CSVs, dataframes
    MULTIMODAL = "multimodal" # Combination of two or more modalities
    EMBEDDING = "embedding"   # Vector input/output

    @classmethod
    def list(cls) -> list[str]:
        return [m.value for m in cls]


class ModelTaskType(str, Enum):
    """
    Represents high-level task types that models can perform.
    """
    GENERATION = "generation"             # Text or sequence generation
    CLASSIFICATION = "classification"     # Label or category prediction
    EMBEDDING = "embedding"               # Vector representation of input
    TRANSLATION = "translation"           # Text translation between languages
    TRANSCRIPTION = "transcription"       # Speech/audio to text
    TEXT_TO_SPEECH = "text_to_speech"     # Text to audio generation

    IMAGE_GENERATION = "image_generation" # Text-to-image generation
    VIDEO_GENERATION = "video_generation" # Text-to-video generation
    AUDIO_GENERATION = "audio_generation"                       # Non-speech audio generation/dialogue

    @classmethod
    def list(cls) -> list[str]:
        return [t.value for t in cls]



# --- Define Model Schema ---


class ModelSpec(BaseModel):
    name: str = Field(..., description="Model name, e.g., gpt-4o, llama3.")
    task: ModelTaskType = Field(..., description="Primary task type of the model.")
    modalities: List[Modality] = Field(
        ..., description="Supported modalities (text, image, code, etc.)."
    )
    description: Optional[str] = Field(
        None, description="Optional description of the model."
    )
    context_window: Optional[int] = Field(None, description="Context window in tokens.")
    max_completion_tokens: Optional[int] = Field(
        None, description="Maximum completion tokens."
    )


# --- Define Provider Schema ---


class ProviderModels(BaseModel):
    provider: ProviderType = Field(
        ..., description="Name of the provider, e.g., openai, groq, etc."
    )
    models: List[ModelSpec] = Field(
        ..., description="List of models available under this provider."
    )


# --- Example Repository ---

models_repository: List[ProviderModels] = [
    ProviderModels(
        provider=ProviderType.OPENAI,
        models=[
            ModelSpec(
                name="gpt-4.5-preview",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT, Modality.CODE],
                description="Largest and most capable GPT model.",
                context_window=128000,
                max_completion_tokens=4096,
            ),
            ModelSpec(
                name="gpt-4o",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT, Modality.CODE],
                description="Fast, intelligent, flexible GPT model.",
                context_window=128000,
                max_completion_tokens=4096,
            ),
            ModelSpec(
                name="gpt-4o-mini",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT, Modality.CODE],
                description="Fast, affordable small model for focused tasks.",
                context_window=128000,
                max_completion_tokens=4096,
            ),
            ModelSpec(
                name="gpt-4-turbo",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT, Modality.CODE],
                description="An older high-intelligence GPT model.",
                context_window=128000,
                max_completion_tokens=4096,
            ),
            ModelSpec(
                name="gpt-3.5-turbo",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT],
                description="Legacy GPT model for cheaper chat and non-chat tasks.",
                context_window=16384,
                max_completion_tokens=4096,
            ),
            ModelSpec(
                name="text-embedding-3-large",
                task=ModelTaskType.EMBEDDING,
                modalities=[Modality.TEXT],
                description="Most capable embedding model.",
                context_window=None,
                max_completion_tokens=None,
            ),
            ModelSpec(
                name="omni-moderation-latest",
                task=ModelTaskType.CLASSIFICATION,
                modalities=[Modality.TEXT, Modality.IMAGE],
                description="Identify potentially harmful content in text and images.",
                context_window=None,
                max_completion_tokens=None,
            ),
        ],
    ),
    ProviderModels(
        provider=ProviderType.GROQ,
        models=[
            ModelSpec(
                name="llama-3.3-70b-versatile",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT],
                description="Meta's versatile 70B parameter model.",
                context_window=128000,
                max_completion_tokens=32768,
            ),
            ModelSpec(
                name="llama-3.1-8b-instant",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT],
                description="Meta's 8B parameter instant model.",
                context_window=128000,
                max_completion_tokens=8192,
            ),
            ModelSpec(
                name="llama-guard-3-8b",
                task=ModelTaskType.CLASSIFICATION,
                modalities=[Modality.TEXT],
                description="Meta's guard model for moderation and classification.",
                context_window=8192,
                max_completion_tokens=None,
            ),
            ModelSpec(
                name="llama3-70b-8192",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT],
                description="Meta's 70B model with 8k context window.",
                context_window=8192,
                max_completion_tokens=None,
            ),
            ModelSpec(
                name="llama3-8b-8192",
                task=ModelTaskType.GENERATION,
                modalities=[Modality.TEXT],
                description="Meta's 8B model with 8k context window.",
                context_window=8192,
                max_completion_tokens=None,
            ),
            ModelSpec(
                name="whisper-large-v3",
                task=ModelTaskType.CLASSIFICATION,
                modalities=[Modality.TEXT],
                description="OpenAI's general-purpose speech recognition model.",
                context_window=None,
                max_completion_tokens=None,
            ),
            ModelSpec(
                name="whisper-large-v3-turbo",
                task=ModelTaskType.CLASSIFICATION,
                modalities=[Modality.TEXT],
                description="Turbo version of OpenAI's Whisper speech recognition model.",
                context_window=None,
                max_completion_tokens=None,
            ),
        ],
    ),
]


# --- ModelSpecRepo class ---


class ModelSpecRepo:
    def __init__(self, repository: Optional[List[ProviderModels]] = None):
        self.repository = repository or models_repository

    def get_model_by_name(self, name: str) -> Optional[ModelSpec]:
        for provider in self.repository:
            for model in provider.models:
                if model.name == name:
                    return model
        return None

    def get_models_by_provider(self, provider_name: ProviderType) -> List[ModelSpec]:
        for provider in self.repository:
            if provider.provider == provider_name:
                return provider.models
        return []

    def list_all_models(self) -> List[ModelSpec]:
        all_models = []
        for provider in self.repository:
            all_models.extend(provider.models)
        return all_models

    def get_models_by_task(self, task_type: ModelTaskType) -> List[ModelSpec]:
        models = []
        for provider in self.repository:
            for model in provider.models:
                if model.task == task_type:
                    models.append(model)
        return models


# Example usage
if __name__ == "__main__":
    # Example: Use ModelSpecRepo
    repo = ModelSpecRepo()
    print("\nFetching model by name 'gpt-4o':")
    model = repo.get_model_by_name("gpt-4o")
    print(model)

    print("\nListing all generation models:")
    for model in repo.get_models_by_task(ModelTaskType.GENERATION):
        print(f"- {model.name}")
