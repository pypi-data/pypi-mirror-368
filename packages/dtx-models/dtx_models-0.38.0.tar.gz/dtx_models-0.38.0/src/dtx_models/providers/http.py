from enum import Enum
from typing import Any, Callable, Dict, Literal, Optional, Union
from dtx_models.utils.urls import url_2_name

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    field_serializer,
    field_validator,
)


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class BaseHttpProvider(BaseModel):
    """Base class for common HTTP provider attributes."""

    max_retries: int = Field(
        4, ge=0, description="Maximum number of retries for failed requests."
    )
    validate_response: Optional[Union[str, Callable[[int], bool]]] = Field(
        None, description="Validation function for HTTP response status."
    )
    transform_request: Optional[Union[str, Dict[str, Any]]] = Field(
        None, description="Template or mapping to modify request before sending."
    )
    transform_response: Optional[Union[str, Dict[str, Any]]] = Field(
        None, description="Transformation logic for processing API responses."
    )

    example_response: Optional[str] = Field(
        None, description="Example response dumped as sample if available"
    )


class StructuredHttpProviderConfig(BaseHttpProvider):
    """Defines an HTTP request provider with structured fields (URL, method, headers, body)."""

    type: Literal["http-parsed"] = Field("http-parsed", description="Provider type discriminator.")
    url: str = Field(..., description="The HTTP endpoint URL.")
    method: HttpMethod = Field(..., description="HTTP method.")
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="HTTP headers."
    )
    body: Optional[Union[str, Dict[str, Any]]] = Field(
        None, description="HTTP request body as JSON or a form-urlencoded string."
    )

    @field_serializer("method")
    def serialize_http_method(self, method: HttpMethod) -> Optional[str]:
        """Serialize the HTTP method to a string."""
        return str(method.value) if method else None

    @field_validator("url", mode="before")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        """Validate that the URL is well-formed."""
        try:
            HttpUrl(value)  # Validate the URL format
        except ValueError as e:
            raise ValueError(f"Invalid base_url: {value}") from e
        return value

    @field_validator("body", mode="before")
    @classmethod
    def validate_body(
        cls, value: Optional[Union[str, Dict[str, Any]]]
    ) -> Optional[Union[str, Dict[str, Any]]]:
        """Ensure body is either a JSON dictionary or a form-urlencoded string."""
        if value is not None and not isinstance(value, (str, dict)):
            raise ValueError(
                "Body must be a dictionary (JSON) or a string (form-urlencoded)."
            )
        return value


    def get_name(self) -> str:
        """Generate a name from the URL using scheme:host:port:/path"""
        return url_2_name(self.url, level=3)


class RawHttpProviderConfig(BaseHttpProvider):
    """Defines an HTTP request provider using raw_request instead of structured fields."""

    type: Literal["http-raw"] = Field("http-raw", description="Provider type discriminator.")
    raw_request: str = Field(..., description="Full raw HTTP request in text format.")
    use_https: bool = Field(default=False, description="Whether to use HTTPS.")

    @field_validator("raw_request", mode="before")
    @classmethod
    def validate_raw_request(cls, value: str) -> str:
        """Ensure raw_request is a valid string."""
        if not isinstance(value, str):
            raise ValueError("Raw HTTP request must be a string.")
        return value

    def get_name(self) -> str:
        """
        Extract the HTTP method and path from the first line of the raw request.
        Returns something like 'GET /api/v1/resource'.
        """
        try:
            first_line = self.raw_request.strip().splitlines()[0]
            parts = first_line.split()
            method = parts[0] if len(parts) > 0 else "UNKNOWN"
            path = parts[1] if len(parts) > 1 else "/"
            return f"{method} {path}"
        except Exception:
            return "INVALID RAW REQUEST"


class HttpProvider(BaseModel):
    provider: Literal["http"] = Field(
        "http", description="Provider ID, always set to 'http'."
    )
    config: StructuredHttpProviderConfig | RawHttpProviderConfig


class BaseHttpProviderResponse(BaseModel):
    """
    Represents a standardized response format for HTTP providers.

    - `mutations`: Stores any changes or replacements applied to the request.
    - `request`: Stores the raw request sent (either as a string or a structured dictionary).
    - `response`: Stores the raw response received (either as a string or a structured dictionary).
    """

    mutations: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Replacements performed in the request"
    )
    # request: Optional[Union[str, Dict[str, Any]]] = Field(
    #     default_factory=dict, description="Request Sent"
    # )
    response: Optional[Union[str, Dict[str, Any]]] = Field(
        default_factory=dict, description="Response Received"
    )


# class Providers(BaseModel):
#     providers: List[HttpProvider]
