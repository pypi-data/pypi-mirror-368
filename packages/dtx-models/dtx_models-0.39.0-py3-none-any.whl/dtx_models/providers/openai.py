import os
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field, field_serializer, model_validator
from ..providers.models_spec import ModelTaskType, Modality

"""
id: openai
config:
  model: gpt-4o

"""


""" 
id: openai
config:
  model: gpt-4o
  task: generation
  endpoint: https://api.openai.com/v1
  params:
    temperature: 0.7
    top_k: 40
    top_p: 0.9
    repeat_penalty: 1.1
    max_tokens: 512
    num_return_sequences: 1
    extra_params:
      stop: ["###", "User:"]

"""


# --- PARAMETER MODELS ---


class ProviderParams(BaseModel):
    """Optional parameters for fine-tuning model generation behavior."""

    temperature: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Controls randomness in generation (0 = deterministic, 1 = maximum randomness).",
    )
    top_k: Optional[int] = Field(
        None, ge=1, description="Top-k sampling strategy: consider the top k tokens."
    )
    top_p: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Nucleus sampling: consider tokens within the cumulative probability top_p.",
    )
    repeat_penalty: Optional[float] = Field(
        None,
        ge=0,
        description="Penalty applied to repeating tokens to reduce repetition.",
    )
    max_tokens: Optional[int] = Field(
        None, ge=1, description="Maximum number of tokens to generate in the output."
    )
    num_return_sequences: Optional[int] = Field(
        None, ge=1, description="Number of generated sequences to return."
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional, model-specific parameters not explicitly defined.",
    )


# --- BASE PROVIDER CONFIGURATION ---


class BaseProviderConfig(BaseModel):
    """Base configuration for model providers."""

    model: str = Field(
        ..., description="Model name (e.g., gpt-4o, llama3, etc.)"
    )
    task: Optional[ModelTaskType] = Field(
        default=None,
        description="Task type for the model. If not provided, it can be inferred based on the model name.",
    )
    modality: Optional[Modality] = Field(
        default=None,
        description="Modality for the model (e.g., text, image). If not provided, can be inferred.",
    )
    context_window: Optional[int] = Field(
        None, ge=1, description="Context window of the model"
    )
    params: Optional[ProviderParams] = Field(
        None, description="Optional parameters for customizing generation behavior."
    )
    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the server or proxy endpoint.",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API Key to access the endpoint",
    )

    # Maps environment variable names to class attribute names
    env_vars: Dict[str, str] = {}

    @model_validator(mode="after")
    def compute_fields(cls, values):
        if not values.task:
            if "guard" in values.model or "classifier" in values.model:
                values.task = ModelTaskType.CLASSIFICATION
            else:
                values.task = ModelTaskType.GENERATION
        return values

    @field_serializer("task")
    def serialize_task(self, task: ModelTaskType) -> str:
        if task:
            return task.value

    @field_serializer("modality")
    def serialize_modality(self, modality: Modality) -> str:
        if modality:
            return modality.value

    def load_from_env(self):
        """Populate config fields from mapped environment variables."""
        for env_var, attr_name in self.env_vars.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                setattr(self, attr_name, env_value)


# --- OPENAI PROVIDER ---

class OpenaiProviderConfig(BaseProviderConfig):
    type: Literal["openai"] = Field(
        "openai", description="Provider type discriminator."
    )

    endpoint: Optional[str] = Field(
        default="https://api.openai.com/v1",
        description="Base URL of the OpenAI server or proxy endpoint.",
    )

    # Override or extend the env_vars mapping
    env_vars: Dict[str, str] = {
        "OPENAI_API_KEY": "api_key",
        "OPENAI_BASE_URL": "endpoint",
    }

    def get_name(self) -> str:
        """
        Returns the model name as the provider's name.
        """
        return self.model



class OpenaiProvider(BaseModel):
    """Wrapper for OpenAI provider configuration."""

    provider: Literal["openai"] = Field(
        "openai", description="Provider ID, always set to 'openai'."
    )
    config: OpenaiProviderConfig
