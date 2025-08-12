


from typing import Literal, Optional, Dict
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class BedrockClaudeProviderConfig(BaseProviderConfig):
    type: Literal["bedrock_claude"] = Field("bedrock_claude", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="AWS Bedrock endpoint URL (BEDROCK_API_BASE or user-supplied)."
    )
    region: Optional[str] = Field(
        default=None,
        description="AWS region for Bedrock endpoint (e.g., us-east-1)."
    )
    aws_access_key_id: Optional[str] = Field(
        default=None,
        description="AWS Access Key ID (BEDROCK_AWS_ACCESS_KEY_ID)."
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        description="AWS Secret Access Key (BEDROCK_AWS_SECRET_ACCESS_KEY)."
    )
    aws_session_token: Optional[str] = Field(
        default=None,
        description="AWS Session Token (BEDROCK_AWS_SESSION_TOKEN, optional)."
    )
    profile: Optional[str] = Field(
        default=None,
        description="AWS profile name for boto3 session (optional)."
    )
    env_vars: Dict[str, str] = {
        "BEDROCK_API_KEY": "api_key",
        "BEDROCK_API_BASE": "endpoint",
    }

    def get_name(self) -> str:
        return self.model

class BedrockClaudeProvider(BaseModel):
    provider: Literal["bedrock_claude"] = Field("bedrock_claude", description="Provider ID for Claude via Bedrock.")
    config: BedrockClaudeProviderConfig
