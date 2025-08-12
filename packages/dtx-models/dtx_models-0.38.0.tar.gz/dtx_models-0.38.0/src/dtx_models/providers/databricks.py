from typing import Literal, Optional
from pydantic import BaseModel, Field

from ..providers.openai import BaseProviderConfig

class DatabricksProviderConfig(BaseProviderConfig):
    type: Literal["databricks"] = Field("databricks", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL for Databricks API (DATABRICKS_API_BASE or user-supplied)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Databricks (DATABRICKS_API_KEY or Databricks PAT)."
    )
    workspace_id: Optional[str] = Field(
        default=None,
        description="Workspace ID for Databricks (DATABRICKS_WORKSPACE_ID, optional)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version (optional, e.g., '2024-05-01')."
    )

    def get_name(self) -> str:
        return self.model

class DatabricksProvider(BaseModel):
    provider: Literal["databricks"] = Field("databricks", description="Provider ID for Databricks.")
    config: DatabricksProviderConfig
