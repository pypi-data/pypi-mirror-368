from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_serializer

class BaseTactic(BaseModel):
    name: str = Field(description="Name of the Tactic")


class BaseTacticConfig(BaseModel):
    pass

class TacticModule(str, Enum):
    FLIP_ATTACK = "flip_attack"

    def __str__(self):
        return self.value

    @classmethod
    def values(cls) -> List[str]:
        return [mode.value for mode in cls]

    @classmethod
    def descriptions(cls) -> dict:
        return {
            cls.FLIP_ATTACK.value: "Flips letters in the prompt (e.g., 'a' to 'ɐ') to evade filters.",
        }



class TacticWithModesConfig(BaseTacticConfig):
    modes: Optional[List[str]] = Field(
        default_factory=list, description="Jailbreak Mode Config"
    )


class TacticWithLanguagesConfig(BaseTacticConfig):
    languages: Optional[List[str]] = Field(
        default_factory=list, description="Languages to perform transformation"
    )


class PromptMutationTactic(BaseTactic):
    name: TacticModule = Field(description="Name of the Tactic")
    config: Optional[TacticWithModesConfig | TacticWithLanguagesConfig] = Field(
        default=None,
        description="Configuration specific to the jailbreak Tactic",
    )

    @field_serializer("name")
    def serialize_eval_model_type(self, name: TacticModule) -> str:
        return name.value
