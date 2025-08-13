import os

from typing import Literal, Optional
from pydantic import BaseModel, Field
from .openai import OpenaiProviderConfig
from typing import Dict
from pydantic import model_validator



class LitellmProviderConfig(OpenaiProviderConfig):
    """
    Config for LiteLLM, a unified gateway to multiple LLM providers.
    The model should be in the format: <provider>/<model-name>
    e.g., groq/mixtral-8x7b or openai/gpt-4o
    """

    type: Literal["litellm"] = Field("litellm", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for LiteLLM proxy or passthrough target."
    )

    # ENV variable map per upstream provider
    env_vars: Dict[str, Dict[str, str]] = {
        "openai": {
            "OPENAI_API_KEY": "api_key",
            "OPENAI_BASE_URL": "endpoint",
        },
        "groq": {
            "GROQ_API_KEY": "api_key",
            "GROQ_BASE_URL": "endpoint",
        },
        "anthropic": {
            "ANTHROPIC_API_KEY": "api_key",
            "ANTHROPIC_BASE_URL": "endpoint",
        },
        "mistral": {
            "MISTRAL_API_KEY": "api_key",
            "MISTRAL_BASE_URL": "endpoint",
        },
        "cohere": {
            "COHERE_API_KEY": "api_key",
            "COHERE_BASE_URL": "endpoint",
        },
        "together": {
            "TOGETHER_API_KEY": "api_key",
            "TOGETHER_BASE_URL": "endpoint",
        },
        "ollama": {
            "OLLAMA_BASE_URL": "endpoint",  # No API key for Ollama
        },
    }

    @model_validator(mode="after")
    def load_env_for_multiprovider(cls, values):
        model = values.model

        if not model or "/" not in model:
            return values

        provider_name, _ = model.split("/", 1)
        provider_env = values.env_vars.get(provider_name)

        if provider_env:
            for env_key, attr in provider_env.items():
                env_val = os.getenv(env_key)
                if env_val is not None:
                    setattr(values, attr, env_val)

        return values

    def get_name(self) -> str:
        """Returns the full model name (e.g. 'groq/mixtral-8x7b')."""
        return self.model



class LitellmProvider(BaseModel):
    """Wrapper for OpenAI provider configuration."""

    provider: Literal["litellm"] = Field(
        "litellm", description="Provider ID, always set to 'openai'."
    )
    config: LitellmProviderConfig
