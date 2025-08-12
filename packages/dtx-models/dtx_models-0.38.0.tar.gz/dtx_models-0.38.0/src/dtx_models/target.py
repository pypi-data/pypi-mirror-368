from typing import Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, HttpUrl


class BaseTarget(BaseModel):
    """
    Base class for all AI providers in dtx.

    Attributes:
        id (str): Unique identifier for the provider.
        config (Optional[Dict[str, Union[str, int, float, List[str]]]]):
            Configuration options such as API keys, temperature, max tokens, etc.
    """

    id: str = Field(
        description="Unique provider identifier (e.g., 'openai:gpt-4o-mini')"
    )
    config: Optional[Dict[str, Union[str, int, float, List[str]]]] = Field(
        default_factory=dict,
        description="Optional configuration settings for the provider.",
    )


class OpenAITarget(BaseTarget):
    """
    OpenAI provider for GPT-based models.

    Example:
    ```yaml
    providers:
      - id: openai:gpt-4o-mini
        config:
          temperature: 0.7
          max_tokens: 150
    ```
    """

    id: str = Field(default="openai:gpt-4o-mini", description="OpenAI model identifier")
    config: Dict[str, Union[str, int, float, List[str]]] = Field(
        default_factory=lambda: {"temperature": 0.7, "max_tokens": 150}
    )


class AnthropicTarget(BaseTarget):
    """
    Anthropic provider for Claude models.

    Example:
    ```yaml
    providers:
      - id: anthropic:messages:claude-3-7-sonnet
        config:
          max_tokens: 1000
    ```
    """

    id: str = Field(
        default="anthropic:messages:claude-3-7-sonnet",
        description="Anthropic model identifier",
    )
    config: Dict[str, Union[str, int]] = Field(
        default_factory=lambda: {"max_tokens": 1000}
    )


class HTTPTarget(BaseTarget):
    """
    Generic HTTP provider for API-based integrations.

    Example:
    ```yaml
    providers:
      - id: https://api.example.com/v1/chat/completions
        config:
          headers:
            Authorization: "Bearer your_api_key"
    ```
    """

    id: HttpUrl = Field(description="API endpoint URL")
    config: Dict[str, Union[str, Dict[str, str]]] = Field(
        default_factory=lambda: {"headers": {"Authorization": "Bearer your_api_key"}}
    )


class LocalPythonTarget(BaseTarget):
    """
    Custom Python-based provider.

    Example:
    ```yaml
    providers:
      - id: file://path/to/custom_provider.py
    ```
    """

    id: str = Field(
        description="Path to the custom Python script (e.g., file://path/to/custom_provider.py)"
    )


class ShellCommandTarget(BaseTarget):
    """
    Target for executing shell commands.

    Example:
    ```yaml
    providers:
      - id: "exec: python chain.py"
    ```
    """

    id: str = Field(
        description="Shell command to execute (e.g., 'exec: python chain.py')"
    )


class WebSocketTarget(BaseModel):
    """
    WebSocket provider for real-time AI model interactions.

    Example:
    ```yaml
    providers:
      - id: ws://example.com/ws
        config:
          messageTemplate: '{"prompt": "{{prompt}}"}'
    ```
    """

    id: AnyUrl = Field(description="WebSocket URL (supports ws:// and wss://)")
    config: Optional[Dict[str, str]] = Field(
        default_factory=lambda: {"messageTemplate": '{"prompt": "{{prompt}}"}'}
    )


class CustomJSTarget(BaseTarget):
    """
    JavaScript-based custom provider.

    Example:
    ```yaml
    providers:
      - id: file://path/to/custom_provider.js
    ```
    """

    id: str = Field(
        description="Path to the JavaScript file (e.g., file://path/to/custom_provider.js)"
    )


class OpenRouterTarget(BaseTarget):
    """
    OpenRouter provider for accessing multiple AI models via a unified API.

    Example:
    ```yaml
    providers:
      - id: openrouter:mistral/7b-instruct
    ```
    """

    id: str = Field(
        default="openrouter:mistral/7b-instruct",
        description="OpenRouter model identifier",
    )


class GoogleVertexAITarget(BaseTarget):
    """
    Google Vertex AI provider for Gemini models.

    Example:
    ```yaml
    providers:
      - id: vertex:gemini-pro
    ```
    """

    id: str = Field(
        default="vertex:gemini-pro", description="Google Vertex AI model identifier"
    )


class AWSBedrockTarget(BaseTarget):
    """
    AWS Bedrock provider for various hosted models.

    Example:
    ```yaml
    providers:
      - id: bedrock:us.meta.llama3-2-90b-instruct-v1:0
    ```
    """

    id: str = Field(
        default="bedrock:us.meta.llama3-2-90b-instruct-v1:0",
        description="AWS Bedrock model identifier",
    )


class HuggingFaceTarget(BaseTarget):
    """
    Hugging Face provider for model inference.

    Example:
    ```yaml
    providers:
      - id: huggingface:text-generation:gpt2
    ```
    """

    id: str = Field(
        default="huggingface:text-generation:gpt2",
        description="Hugging Face model identifier",
    )


class ManualInputTarget(BaseTarget):
    """
    Manual input provider for CLI-based interaction.

    Example:
    ```yaml
    providers:
      - id: dtx:manual-input
    ```
    """

    id: str = Field(
        default="dtx:manual-input", description="Manual input provider identifier"
    )


if __name__ == "__main__":
    # Example usage
    def example_usage():
        providers = [
            OpenAITarget(),
            AnthropicTarget(),
            HTTPTarget(id="https://api.example.com/v1/chat/completions"),
            LocalPythonTarget(id="file://path/to/custom_provider.py"),
            WebSocketTarget(id="ws://example.com/ws"),
            CustomJSTarget(id="file://path/to/custom_provider.js"),
            AWSBedrockTarget(),
            HuggingFaceTarget(),
            ManualInputTarget(),
        ]

        for provider in providers:
            print(provider.model_dump_json())

    example_usage()
