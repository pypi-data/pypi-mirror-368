import re
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .base import (
    BasePrompTemplateParam,
    BasePromptTemplateConversation,
    BasePromptTemplateRepo,
)


class LangchainHubPromptMetadata(BaseModel):
    id: str
    name: str
    owner: Optional[str] = None
    description: Optional[str] = None
    readme: Optional[str] = None
    tags: List[str] = []
    last_commit_hash: Optional[str] = None
    full_name: str


class LangchainHubPromptParam(BasePrompTemplateParam):
    pass


class LangchainHubPrompt(BasePromptTemplateConversation):
    metadata: LangchainHubPromptMetadata


class LanghubPromptTemplateConfig(BaseModel):
    full_name: str = Field(description="Repo Full Name")
    prompt: Optional[LangchainHubPrompt] = Field(
        default=None, description="Template Details"
    )
    params: Optional[List[LangchainHubPromptParam]] = Field(
        None,
        description="Optional list of parameters that can be replaced with values.",
    )

    @classmethod
    def from_full_path(cls, full_path: str) -> "LanghubPromptTemplateConfig":
        """
        Factory method to extract full_name from full_path URL or path.
        Example input:
            - 'https://smith.langchain.com/hub/rlm/rag-prompt'
            - '/rlm/rag-prompt'
            - 'rlm/rag-prompt'
        """
        pattern = r"(?:https?://smith\.langchain\.com/hub)?/?(.+/.+)"
        match = re.search(pattern, full_path.strip())
        if not match:
            raise ValueError(
                "Invalid full path format.\n"
                "Example: 'https://smith.langchain.com/hub/rlm/rag-prompt' or '/rlm/rag-prompt'"
            )
        full_name = match.group(1).strip("/")
        return cls(full_name=full_name)


# Concrete implementation for Langhub
class LangHubPromptTemplate(BasePromptTemplateRepo):
    provider: Literal["langhub"] = Field(
        "langhub", description="Prompt ID, always set to 'langhub'."
    )
    config: LanghubPromptTemplateConfig

    def get_template(self) -> BasePromptTemplateConversation:
        if not self.config.prompt:
            raise ValueError("Prompt template is not configured.")
        return self.config.prompt

    def get_params(self) -> Optional[List[LangchainHubPromptParam]]:
        return self.config.params


class LangHubPromptTemplates(BaseModel):
    prompts: List[LangHubPromptTemplate]
