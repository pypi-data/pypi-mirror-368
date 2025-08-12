from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from ...prompts import BaseMultiTurnConversation


class PromptsRepoType(str, Enum):
    LANGHUB = "langhub"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class BasePrompTemplateParam(BaseModel):
    """
    Represents a parameter to be used in a request to a Gradio API.
    """

    name: str = Field(..., description="The name of the parameter.")
    value: Optional[Union[str, int, bool, float, list, tuple, dict]] = Field(
        None, description="The value of the parameter to be sent in the API request."
    )


class BasePromptTemplateConversation(BaseModel):
    conversation: BaseMultiTurnConversation
    input_variables: List[str]


# Base abstract repository
class BasePromptTemplateRepo(BaseModel, ABC):
    id: str = Field(..., description="Prompt ID")

    @abstractmethod
    def get_template(self) -> BasePromptTemplateConversation:
        """Retrieve the base prompt template."""
        pass

    @abstractmethod
    def get_params(self) -> Optional[List[BasePrompTemplateParam]]:
        """Retrieve the list of parameters for the prompt template."""
        pass
