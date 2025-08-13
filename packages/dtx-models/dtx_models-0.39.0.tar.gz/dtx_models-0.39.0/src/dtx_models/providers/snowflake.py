from typing import Literal, Optional
from pydantic import BaseModel, Field
from ..providers.openai import BaseProviderConfig

class SnowflakeProviderConfig(BaseProviderConfig):
    type: Literal["snowflake"] = Field("snowflake", description="Provider type discriminator.")

    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the Snowflake Cortex endpoint (SNOWFLAKE_API_BASE)."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for Snowflake Cortex (SNOWFLAKE_API_KEY)."
    )
    account: Optional[str] = Field(
        default=None,
        description="Snowflake account identifier (SNOWFLAKE_ACCOUNT)."
    )
    role: Optional[str] = Field(
        default=None,
        description="Snowflake role (SNOWFLAKE_ROLE)."
    )
    warehouse: Optional[str] = Field(
        default=None,
        description="Snowflake warehouse (SNOWFLAKE_WAREHOUSE)."
    )
    database: Optional[str] = Field(
        default=None,
        description="Snowflake database (SNOWFLAKE_DATABASE)."
    )
    snowflake_schema: Optional[str] = Field(
        default=None,
        description="Snowflake schema (SNOWFLAKE_SCHEMA)."
    )
    api_version: Optional[str] = Field(
        default=None,
        description="API version for Snowflake Cortex (SNOWFLAKE_API_VERSION)."
    )

    def get_name(self) -> str:
        return self.model

class SnowflakeProvider(BaseModel):
    provider: Literal["snowflake"] = Field("snowflake", description="Provider ID for Snowflake Cortex.")
    config: SnowflakeProviderConfig
