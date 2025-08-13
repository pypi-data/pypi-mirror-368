from enum import Enum
from typing import Any, Dict, Literal, Optional
from dtx_models.utils.urls import url_2_name

from pydantic import BaseModel, Field, field_serializer, model_validator
from .openai import BaseProviderConfig 

## Supported Yaml

# """
# ollama:
#   - model: llama3


# ollama:
#   - model: llama3
#     task: text-generation
#     endpoint: http://localhost:11434
#     params:
#       temperature: 1.0
#       top_k: 50
#       top_p: 1.0
#       repeat_penalty: 1.1
#       max_tokens: 512
#       num_return_sequences: 1
#       extra_params:
#         stop: ["###", "User:"]
# """



class OllamaTask(str, Enum):
    """
    Enum for supported Ollama tasks.
    """
    TEXT_GENERATION = "text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    SAFETY_CLASSIFICATION = "safety-classification"

    def __str__(self):
        return self.value

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class OllamaProviderParams(BaseModel):
    """
    Configuration for Ollama model inference parameters.
    """
    temperature: Optional[float] = Field(
        None, ge=0, le=1,
        description="Controls randomness: higher values make output more diverse."
    )
    top_k: Optional[int] = Field(
        None, ge=1,
        description="Top-k sampling: limits selection to top k most likely tokens."
    )
    top_p: Optional[float] = Field(
        None, ge=0, le=1,
        description="Top-p (nucleus) sampling: limits selection to tokens within cumulative probability p."
    )
    repeat_penalty: Optional[float] = Field(
        None, ge=0,
        description="Penalizes repeated tokens in the output."
    )
    max_tokens: Optional[int] = Field(
        None, ge=1,
        description="Maximum number of tokens to generate in the response."
    )
    num_return_sequences: Optional[int] = Field(
        None, ge=1,
        description="Number of output sequences to return for each prompt."
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Custom parameters to be passed directly to the Ollama engine."
    )


class OllamaProviderConfig(BaseProviderConfig):
    """
    Configuration class for using the Ollama model provider (local inference).
    Ollama runs models locally and does not require authentication.
    """

    type: Literal["ollama"] = Field(
        "ollama",
        description="Provider type discriminator. Always set to 'ollama'."
    )

    task: Optional[OllamaTask] = Field(
        default=None,
        description="""
        Specific task type for Ollama models. If not provided, it will be inferred
        based on the model name (e.g., 'guard' implies classification).
        """
    )

    params: Optional[OllamaProviderParams] = Field(
        None,
        description="Optional generation parameters used to control model behavior."
    )

    endpoint: Optional[str] = Field(
        default="http://localhost:11434",
        description="Base URL of the locally running Ollama server."
    )

    # Ollama does not use API keys
    env_vars: Dict[str, str] = {
        "OLLAMA_BASE_URL": "endpoint",
    }

    @model_validator(mode="after")
    def compute_fields(cls, values):
        if not values.task:
            if "guard" in values.model:
                values.task = OllamaTask.TEXT_CLASSIFICATION
            else:
                values.task = OllamaTask.TEXT_GENERATION
        return values

    @field_serializer("task")
    def serialize_task(self, task: OllamaTask) -> str:
        return task.value if task else None

    def get_name(self) -> str:
        """
        Generates a unique name based on the model and endpoint,
        e.g., 'llama3:http:localhost:11434:'
        """
        return f"{self.model}:{url_2_name(self.endpoint, level=3)}"


class OllamaProvider(BaseModel):
    """
    Wrapper class for an Ollama provider instance.
    """
    provider: Literal["ollama"] = Field(
        "ollama",
        description="Provider ID, must be 'ollama'."
    )
    config: OllamaProviderConfig = Field(
        ..., description="Full configuration for the Ollama provider instance."
    )
