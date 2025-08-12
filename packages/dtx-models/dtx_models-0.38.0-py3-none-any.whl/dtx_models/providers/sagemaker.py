from typing import Literal, Optional
from pydantic import BaseModel, Field

from .openai import BaseProviderConfig

class SagemakerProviderConfig(BaseProviderConfig):
    type: Literal["sagemaker"] = Field("sagemaker", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Endpoint URL for AWS Sagemaker (SAGEMAKER_API_BASE or user-supplied)."
    )
    region: Optional[str] = Field(
        default=None,
        description="AWS region for the Sagemaker endpoint (e.g., us-east-1)."
    )
    aws_access_key_id: Optional[str] = Field(
        default=None,
        description="AWS Access Key ID (SAGEMAKER_AWS_ACCESS_KEY_ID)."
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        description="AWS Secret Access Key (SAGEMAKER_AWS_SECRET_ACCESS_KEY)."
    )
    aws_session_token: Optional[str] = Field(
        default=None,
        description="AWS Session Token (SAGEMAKER_AWS_SESSION_TOKEN, optional)."
    )
    profile: Optional[str] = Field(
        default=None,
        description="AWS profile name for boto3 session (optional)."
    )

    def get_name(self) -> str:
        return self.model

class SagemakerProvider(BaseModel):
    provider: Literal["sagemaker"] = Field("sagemaker", description="Provider ID for AWS Sagemaker.")
    config: SagemakerProviderConfig
