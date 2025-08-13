# from enum import Enum
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field, field_serializer, model_validator

from ..providers.openai import BaseProviderConfig  # Assuming this provides basic fields like model, task, params, etc.
from .models_spec import ModelTaskType  # For GENERATION/CLASSIFICATION, etc.


class AnthropicProviderParams(BaseModel):
    temperature: Optional[float] = Field(None, ge=0, le=1, description="Controls randomness in generation.")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum number of tokens to generate.")
    top_k: Optional[int] = Field(None, ge=1, description="Top-k sampling.")
    top_p: Optional[float] = Field(None, ge=0, le=1, description="Nucleus sampling (top-p).")
    stop: Optional[list[str]] = Field(default=None, description="Stop sequences.")
    extra_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional params for Anthropic model.")


class AnthropicProviderConfig(BaseProviderConfig):
    type: Literal["anthropic"] = Field("anthropic", description="Provider type discriminator.")

    model: str = Field(..., description="Anthropic model name (e.g., claude-3-opus-20240229)")
    task: Optional[ModelTaskType] = Field(default=None, description="Task type for the Anthropic model. Inferred if not provided.")
    params: Optional[AnthropicProviderParams] = Field(None, description="Optional parameters for customizing model behavior.")
    endpoint: Optional[str] = Field(
        default="https://api.anthropic.com/v1",
        description="Base URL of the Anthropic endpoint or proxy."
    )
    anthropic_version: Optional[str] = Field(
        default="2023-06-01",
        description="Version of the Anthropic API to use."
    )
    env_vars: Dict[str, str] = {
        "ANTHROPIC_API_KEY": "api_key",
        "ANTHROPIC_API_BASE": "endpoint"
    }

    @model_validator(mode="after")
    def compute_fields(cls, values):
        # Infer default task from model name if not set
        if not values.task:
            if "guard" in values.model or "classification" in values.model:
                values.task = ModelTaskType.CLASSIFICATION
            else:
                values.task = ModelTaskType.GENERATION
        return values

    @field_serializer("task")
    def serialize_task(self, task: ModelTaskType) -> str:
        return task.value

    def get_name(self) -> str:
        # Name based on model, as in Ollama
        return self.model


class AnthropicProvider(BaseModel):
    provider: Literal["anthropic"] = Field("anthropic", description="Provider ID for Anthropic.")
    config: AnthropicProviderConfig
