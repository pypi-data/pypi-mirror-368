from typing import Literal, Optional, Dict

from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig


class GroqProviderConfig(BaseProviderConfig):
    type: Literal["groq"] = Field("groq", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default="https://api.groq.com/v1",
        description="Base URL of the Groq server or proxy endpoint.",
    )

    # Define environment variable mappings specific to Groq
    env_vars: Dict[str, str] = {
        "GROQ_API_KEY": "api_key",
        "GROQ_BASE_URL": "endpoint",
    }

    def get_name(self) -> str:
        """
        Returns the model name as the provider's name.
        """
        return self.model



class GroqProvider(BaseModel):
    """Wrapper for Groq provider configuration."""

    provider: Literal["groq"] = Field(
        "groq", description="Provider ID, always set to 'groq'."
    )
    config: GroqProviderConfig
