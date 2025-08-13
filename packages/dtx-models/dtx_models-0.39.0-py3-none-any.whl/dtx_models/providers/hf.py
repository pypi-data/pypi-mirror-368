import os
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, field_serializer, model_validator

from ..evaluator import EvaluatorInScope
from ..prompts import SupportedFormat
from .base import BaseProviderConfigWithEnvLoader

class HuggingFaceTask(str, Enum):
    """Supported HuggingFace task types."""

    TEXT_GENERATION = "text-generation"
    TEXT2TEXT_GENERATION = "text2text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    TOKEN_CLASSIFICATION = "token-classification"
    FEATURE_EXTRACTION = "feature-extraction"
    SENTENCE_SIMILARITY = "sentence-similarity"
    FILL_MASK = "fill-mask"


class ClassificationModelScope(str, Enum):
    """Scope in which classification models operate."""

    PROMPT = "prompt"
    RESPONSE = "response"
    CONVERSATION = "conversation"


class DType(str, Enum):
    """Supported data types for inference computation."""

    FLOAT16 = "float16"
    BFLOAT16 = "bfloat16"
    FLOAT32 = "float32"


class HFEndpoint(BaseModel):
    """Configuration for specifying a HuggingFace Inference API endpoint."""

    api_endpoint: Optional[HttpUrl] = Field(
        None, description="Custom API endpoint for the model."
    )
    api_key: Optional[str] = Field(
        None, description="Your HuggingFace API key."
    )


class HuggingFaceProviderParams(BaseModel):
    """Generation and inference parameters for HuggingFace models."""

    temperature: Optional[float] = Field(
        None, ge=0, le=1,
        description="Controls randomness in generation."
    )
    top_k: Optional[int] = Field(
        None, ge=1,
        description="Controls diversity via top-k sampling."
    )
    top_p: Optional[float] = Field(
        None, ge=0, le=1,
        description="Controls diversity via nucleus (top-p) sampling."
    )
    repetition_penalty: Optional[float] = Field(
        None, ge=0,
        description="Penalty for repeated tokens."
    )
    max_new_tokens: Optional[int] = Field(
        None, ge=1,
        description="Maximum number of new tokens to generate."
    )
    max_time: Optional[float] = Field(
        None, ge=0,
        description="Maximum allowed time (in seconds) for model to respond."
    )
    return_full_text: Optional[bool] = Field(
        None, description="Whether to return full input + output text."
    )
    num_return_sequences: Optional[int] = Field(
        None, ge=1,
        description="Number of output sequences to return."
    )
    do_sample: Optional[bool] = Field(
        None, description="Whether to enable sampling."
    )
    use_cache: Optional[bool] = Field(
        None, description="Whether to enable model caching."
    )
    wait_for_model: Optional[bool] = Field(
        None, description="Whether to wait for model if not immediately available."
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        None, description="Additional parameters for fine-tuning inference."
    )
    dtype: Optional[DType] = Field(
        DType.BFLOAT16, description="Computation precision (data type)."
    )

    @field_serializer("dtype")
    def serialize_dtype(self, dtype: DType) -> str:
        return dtype.value if dtype else dtype


class HuggingFaceProviderConfig(BaseProviderConfigWithEnvLoader):
    type: Literal["huggingface"] = Field("huggingface", description="Provider type discriminator.")
    model: str = Field(..., description="HuggingFace model name.")
    task: HuggingFaceTask = Field(..., description="Task type for the HuggingFace model.")
    params: Optional[HuggingFaceProviderParams] = Field(
        None, description="Configuration parameters for HuggingFace model."
    )
    endpoint: Optional[HFEndpoint] = Field(
        None, description="HuggingFace API endpoint configuration."
    )

    env_vars: Dict[str, str] = {
        "HF_API_KEY": "endpoint.api_key",
        "HF_API_ENDPOINT": "endpoint.api_endpoint",
    }

    support_multi_turn: bool = Field(
        default=False,
        description="Does it support Multi Turn",
    )
    supported_input_format: Optional[SupportedFormat] = Field(
        default=SupportedFormat.TEXT,
        description="Supported Input format",
    )
    classification_model_scope: Optional[ClassificationModelScope] = Field(
        default=ClassificationModelScope.CONVERSATION,
        description="Scope of classification model - prompt, response, or whole conversation",
    )
    id: Optional[str] = Field(
        None,
        description="HuggingFace model identifier computed as 'huggingface:<task>:<model>'",
    )
    preferred_evaluator: Optional[EvaluatorInScope] = Field(
        None,
        description="Preferred Evaluator for the provider",
    )

    def load_from_env(self):
        """Explicitly load environment variables into known config fields."""
        api_key = os.getenv("HF_API_KEY")
        api_endpoint = os.getenv("HF_API_ENDPOINT")

        if api_key:
            if not self.endpoint:
                self.endpoint = HFEndpoint()
            self.endpoint.api_key = api_key

        elif api_endpoint:
            if not self.endpoint:
                self.endpoint = HFEndpoint()
            self.endpoint.api_endpoint = api_endpoint

    @model_validator(mode="after")
    def compute_id(cls, values):
        if not values.id:
            values.id = f"huggingface:{values.task.value}:{values.model}"
        return values

    @field_serializer("task")
    def serialize_role(self, task: Optional[HuggingFaceTask]) -> Optional[str]:
        return task.value if task else None

    @field_serializer("supported_input_format")
    def serialize_supported_format(self, supported_input_format: Optional[SupportedFormat]) -> Optional[str]:
        return str(supported_input_format) if supported_input_format else None

    @field_serializer("classification_model_scope")
    def serialize_classification_model_scope(self, scope: Optional[ClassificationModelScope]):
        return scope.value if scope else None

    def get_name(self) -> str:
        """Returns the model name as the provider's name."""
        return self.model


class HuggingFaceGuardModelsProviderConfig(HuggingFaceProviderConfig):
    """
    Specialized config for HuggingFace guard/classifier models with JSONPath-based decision rules.
    """

    safe_value: str = Field(
        "",
        description="JSONPath expression indicating the condition for input to be considered safe."
    )

    """
    Example:
    ----------------
    provider = HuggingFaceGuardModelsProviderConfig(safe_value="$.score[?(@ < 0.6)]")
    This checks if all classification scores are below 0.6.
    """


class HFProvider(BaseModel):
    """
    Wrapper for a single HuggingFace provider configuration instance.
    """

    provider: Literal["huggingface"] = Field(
        "huggingface",
        description="Provider ID. Always 'huggingface'."
    )
    config: HuggingFaceProviderConfig = Field(
        ..., description="Configuration for the selected HuggingFace model."
    )


class HFModels(BaseModel):
    """
    Wrapper for a collection of HuggingFace models (standard + guard models).
    """

    huggingface: List[Union[HuggingFaceProviderConfig, HuggingFaceGuardModelsProviderConfig]] = Field(
        default_factory=list,
        description="List of HuggingFace models available for selection or inference."
    )
