from typing import Any, Dict, List, Literal, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator

from ..utils.urls import url_2_name 


from .base import ProviderType


class GradioApiSignatureParam(BaseModel):
    """
    Represents a single parameter for a Gradio API signature.
    """

    name: str = Field(..., description="Name of the parameter.")
    has_default_value: bool = Field(
        ..., description="Indicates if the parameter has a default value."
    )
    default_value: Optional[Union[str, int, bool, float, list]] = Field(
        None,
        description="The default value of the parameter, which can be a string, integer, boolean, or list.",
    )
    python_type: str = Field(
        ...,
        description="The Python type of the parameter (e.g., str, int, bool, or a Literal).",
    )

    @field_validator("default_value", mode="before")
    @classmethod
    def validate_default_value(cls, value):
        """
        Ensures the default_value is of the correct type.
        - If it's a list, pick the first element if possible.
        - If it's an empty list, return `None`.
        """
        if isinstance(value, list):
            return (
                value[0] if value else None
            )  # Take the first element or None if empty
        return value  # Otherwise, keep it as it is


class GradioApiSignatureParams(BaseModel):
    """
    A wrapper model to hold multiple API signature parameters.
    """

    params: List[GradioApiSignatureParam] = Field(
        ..., description="List of API signature parameters."
    )


class GradioApiSpec(BaseModel):
    """
    Represents a Gradio API specification, including the API name and its parameters.
    """

    api_name: str = Field(..., description="The endpoint path of the API.")
    params: List[GradioApiSignatureParam] = Field(
        default_factory=list, description="List of parameters required by the API."
    )
    # response: Dict[str, Any] = Field(
    #     default_factory=dict, description="The expected response structure."
    # )


class GradioApiSpecs(BaseModel):
    """
    Contains multiple Gradio API specifications.
    """

    apis: List[GradioApiSpec] = Field(
        default_factory=list, description="List of API specifications."
    )


class GradioProviderApiParam(BaseModel):
    """
    Represents a parameter to be used in a request to a Gradio API.
    """

    name: str = Field(..., description="The name of the parameter.")
    value: Optional[Union[str, int, bool, float, list, tuple, dict]] = Field(
        None, description="The value of the parameter to be sent in the API request."
    )


class GradioResponseParserSignature(BaseModel):
    """
    Signature based parser response
    """

    parser_type: Literal["signature"] = Field("signature", description="")
    content_type: Optional[str] = Field(
        default="text",
        description="Content type str, array etc.",
        examples=["json", "jsonl", "text", "array"],
    )
    location: Optional[List[Union[str, int]]] = Field(
        None, description="Location of the response as sequence of integers"
    )


class GradioProviderApi(BaseModel):
    """
    Represents a Gradio API request, including its path and parameters.
    """

    path: str = Field(..., description="The API endpoint path.")
    params: Optional[List[GradioProviderApiParam]] = Field(
        None, description="Optional list of parameters for the API request."
    )
    transform_response: Optional[
        Union[str, GradioResponseParserSignature, Dict[str, Any]]
    ] = Field(
        None, description="Logic to extract Assistant Response from Gradio Response"
    )


class GradioProviderConfig(BaseModel):
    """
    Configuration model for a Gradio API provider.
    Supports both standard URLs and Hugging Face Space identifiers.
    """

    type: Literal["gradio"] = Field("gradio", description="Provider type discriminator.")

    url: str = Field(
        ...,
        description="The base URL of the Gradio API provider or a Hugging Face Space ID.",
    )

    apis: Optional[List[GradioProviderApi]] = Field(
        default_factory=list,
        description="Optional list of APIs available for testing."
    )

    @field_validator("url", mode="before")
    @classmethod
    def validate_url_or_hf_space(cls, value: str) -> str:
        try:
            _ = urlparse(value)
            return value
        except Exception:
            raise ValueError(
                f"Invalid URL or Hugging Face Space identifier: '{value}'. "
                "Provide a valid URL (https://example.com) or a Hugging Face Space in 'org/app' format."
            )

    def get_name(self) -> str:
        """
        Returns a name derived from the URL, limited to 3 path levels.
        """
        return url_2_name(self.url, level=3)


class GradioProvider(BaseModel):
    """
    Represents a Gradio API provider, including its configuration.
    """

    provider: Literal["gradio"] = Field(
        ProviderType.GRADIO.value, description="Provider ID, always set to 'gradio'."
    )
    config: GradioProviderConfig = Field(
        ..., description="Configuration details for the Gradio API provider."
    )


class GradioProviders(BaseModel):
    providers: List[GradioProvider]
