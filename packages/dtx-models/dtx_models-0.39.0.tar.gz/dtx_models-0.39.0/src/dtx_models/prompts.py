import hashlib
import json
from enum import Enum
from collections import defaultdict
from statistics import mean
from typing import Any, Dict, Iterator, List, Optional, Union
from pydantic import (
    BaseModel, 
    ConfigDict,
    Field, 
    field_serializer,
    model_validator
)

from .exceptions import EntityNotFound
from .evaluator import (
    AnyKeywordBasedPromptEvaluation,
    ModelBasedPromptEvaluation, 
    ModuleBasedPromptEvaluation
)
from .evaluator import CriteriaBasedPromptEvaluation


# Define allowed roles
# RoleType = Literal["USER", "ASSISTANT", "SYSTEM"]


class RoleType(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class SupportedFormat(str, Enum):
    TEXT = "text"
    OPENAI = "openai"
    ALPACA = "alpaca"
    CHATML = "chatml"
    VICUNA = "vicuna"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]

class BaseTestPrompt(BaseModel):
    pass 

class BaseTestStrPrompt(BaseTestPrompt):
    prompt: str = Field(
        description="Prompt to achieve the goal. "
        "Prompt can have variable templates that can be replaced with values. "
        "The templates should use curly brackets to specify template variables."
    )
    complexity: int = Field(default=3, description="Default Complexity of the Prompt, range 1-10, Low<=4, 4 <Medium < 8, High>=8")
    jailbreak: bool = Field(default=False, description="Does Prompt Emloy jailbreak technique")
    unsafe: bool = Field(default=True, description="Is the prompt unsafe. Default True")



class Turn(BaseModel):
    role: RoleType = Field(
        ..., description="The role in the conversation (USER, ASSISTANT, SYSTEM)."
    )
    message: Union[str, Any] = Field(
        ..., min_length=1, description="The message content."
    )

    @staticmethod
    def validate_message(value: str) -> str:
        """Ensure the message is not empty or just whitespace."""
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Message cannot be empty or only whitespace.")
        return value

    @field_serializer("role")
    def serialize_role(self, role: RoleType) -> str:
        """Serialize the role enum to a string."""
        return str(role)


class BaseMultiTurnConversation(BaseTestPrompt):
    turns: List[Turn]

    def _filter_turns(self, multi_turn: bool) -> List[Turn]:
        if multi_turn:
            return self.turns
        else:
            filtered_turns = [
                turn for turn in self.turns if turn.role == RoleType.SYSTEM
            ]
            first_user_turn = next(
                (turn for turn in self.turns if turn.role == RoleType.USER), None
            )
            if first_user_turn:
                filtered_turns.append(first_user_turn)
            return filtered_turns

    def to_openai_format(self, multi_turn: bool = True) -> List[Dict[str, str]]:
        """
        Convert the conversation turns into a dictionary format compatible with OpenAI API.
        """
        turns = self._filter_turns(multi_turn)
        return [{"role": turn.role.lower(), "content": turn.message} for turn in turns]

    def to_alpaca_format(self, multi_turn: bool = True) -> str:
        """
        Convert the conversation to Alpaca format (instruction-based structure).
        """
        turns = self._filter_turns(multi_turn)
        return "\n".join(f"### {turn.role}\n{turn.message}" for turn in turns)

    def to_chatml_format(self, multi_turn: bool = True) -> str:
        """
        Convert the conversation to ChatML format (OpenAI ChatML used in models like GPT-4).
        """
        turns = self._filter_turns(multi_turn)
        return "\n".join(
            f"<|{turn.role.lower()}|>{turn.message}<|end|>" for turn in turns
        )

    def to_vicuna_format(self, multi_turn: bool = True) -> str:
        """
        Convert the conversation to Vicuna format (similar to Alpaca but slightly different style).
        """
        turns = self._filter_turns(multi_turn)
        return "".join(
            f"USER: {turn.message}\nASSISTANT: "
            if turn.role == RoleType.USER
            else f"{turn.message}\n"
            for turn in turns
        ).strip()

    def to_text(self, multi_turn: bool = True) -> str:
        """
        Convert the conversation turns into a plain text format.
        """
        turns = self._filter_turns(multi_turn)
        return "\n".join(f"{turn.role}: {turn.message}" for turn in turns)

    def to_format(self, supported_format: SupportedFormat, multi_turn: bool = True):
        """
        Convert the conversation to the requested format.
        """
        if supported_format == SupportedFormat.TEXT:
            return self.to_text(multi_turn)
        elif supported_format == SupportedFormat.OPENAI:
            return self.to_openai_format(multi_turn)
        elif supported_format == SupportedFormat.ALPACA:
            return self.to_alpaca_format(multi_turn)
        elif supported_format == SupportedFormat.CHATML:
            return self.to_chatml_format(multi_turn)
        elif supported_format == SupportedFormat.VICUNA:
            return self.to_vicuna_format(multi_turn)
        else:
            raise ValueError(f"Unsupported format: {supported_format}")

    def last_user_prompt(self) -> str:
        """
        Returns the last USER message from the conversation.
        Raises EntityNotFound if no USER message is found.
        """
        for turn in reversed(self.turns):
            if turn.role == RoleType.USER:
                return turn.message
        raise EntityNotFound("No USER message found in the conversation.")

    def first_user_prompt(self) -> str:
        """
        Returns the last USER message from the conversation.
        Raises EntityNotFound if no USER message is found.
        """
        for turn in self.turns:
            if turn.role == RoleType.USER:
                return turn.message
        raise EntityNotFound("No USER message found in the conversation.")

    def first_system_prompt(self) -> str:
        """
        Returns the last USER message from the conversation.
        Raises EntityNotFound if no USER message is found.
        """
        for turn in self.turns:
            if turn.role == RoleType.SYSTEM:
                return turn.message
        return None

    def last_assistant_response(self) -> str:
        """
        Returns the last ASSISTANT message from the conversation.
        Raises EntityNotFound if no ASSISTANT message is found.
        """
        for turn in reversed(self.turns):
            if turn.role == RoleType.ASSISTANT:
                return turn.message
        raise EntityNotFound("No ASSISTANT message found in the conversation.")

    def has_last_assistant_response(self) -> bool:
        """
        Returns the last ASSISTANT message from the conversation.
        Raises EntityNotFound if no ASSISTANT message is found.
        """
        for turn in reversed(self.turns):
            if turn.role == RoleType.ASSISTANT:
                return True
        return False

    def has_system_turn(self) -> bool:
        """
        Returns a System Turn.
        """
        return self.get_system_turn() is not None

    def get_system_turn(self) -> Turn:
        """
        Returns a System Turn.
        """

        iterator = iter(self.turns)
        for turn in iterator:
            if turn.role in {RoleType.SYSTEM}:
                return turn
        return None

    def get_user_turns(self) -> Iterator[Turn]:
        """
        Returns an iterator over turns with USER or SYSTEM roles.
        If a SYSTEM role is encountered, the next USER role is also included.
        """
        iterator = iter(self.turns)
        for turn in iterator:
            if turn.role in {RoleType.USER}:
                yield turn

    def get_complete_turns(self) -> Iterator[Turn]:
        """
        Yields USER and SYSTEM turns, followed by an ASSISTANT turn.
        If the ASSISTANT response is missing after USER, a placeholder is added.
        SYSTEM is always yielded together with the next USER turn.
        """
        i = 0
        while i < len(self.turns):
            current_turn = self.turns[i]

            if current_turn.role == RoleType.SYSTEM:
                yield current_turn
                i += 1
                if i < len(self.turns) and self.turns[i].role == RoleType.USER:
                    yield self.turns[i]
                    i += 1
                    if i >= len(self.turns) or self.turns[i].role != RoleType.ASSISTANT:
                        yield Turn(role=RoleType.ASSISTANT, message="No Response")
                    else:
                        yield self.turns[i]
                        i += 1
            elif current_turn.role == RoleType.USER:
                yield current_turn
                i += 1
                if i >= len(self.turns) or self.turns[i].role != RoleType.ASSISTANT:
                    yield Turn(role=RoleType.ASSISTANT, message="No Response")
                else:
                    yield self.turns[i]
                    i += 1
            else:
                i += 1

    def add_turn(self, turn: Turn):
        """
        Appends a single turn to the conversation.
        """
        self.turns.append(turn)

    def add_turns(self, turns: List[Turn]):
        """
        Appends multiple turns to the conversation.
        """
        self.turns.extend(turns)


class MultiTurnTestPrompt(BaseMultiTurnConversation):
    id: Optional[str] = Field(
        default=None,
        description="Unique ID of the prompt, auto-generated based on content.",
    )
    evaluation_method: Union[
        ModelBasedPromptEvaluation, AnyKeywordBasedPromptEvaluation
    ] = Field(description="Evaluation method for the prompt.")
    module_name: str = Field(description="Module that has generated the prompt")
    policy: str = Field(default="", description="Policy for which prompt is created for")
    goal: str = Field(default="")
    complexity: int = Field(default=3, description="Default Complexity of the Prompt, range 1-10, Low<=4, 4 <Medium < 8, High>=8")
    jailbreak: bool = Field(default=False, description="Does Prompt Emloy jailbreak technique")
    unsafe: bool = Field(default=True, description="Is the prompt unsafe. Default True")
    strategy: str = Field(
        default="", description="strategy used to generate the prompt"
    )
    base_prompt: str = Field(
        default="",
        description="Base prompt in its most simplistic form that need to be answered by AI AgentInfo. Generally it is the harmful.",
    )

    model_config = ConfigDict(frozen=True)  # Make fields immutable

    def __init__(self, **data):
        """Override init to auto-generate unique ID if not provided."""
        super().__init__(**data)
        object.__setattr__(self, "id", self.compute_unique_id())

    def compute_unique_id(self) -> str:
        """Computes the SHA-1 hash of the prompt as the ID."""
        prompt = str(self.to_openai_format())
        return hashlib.sha1(
            f"{self.strategy}-{self.goal}-{prompt}".encode()
        ).hexdigest()


class StingRayMultiTurnTestPrompt(BaseMultiTurnConversation):
    id: Optional[str] = Field(
        default=None,
        description="Unique ID of the prompt, auto-generated based on content.",
    )
    evaluation_method: Union[
        ModuleBasedPromptEvaluation
    ] = Field(description="Evaluation method for the prompt.")
    module_name: str = Field(description="Module that has generated the prompt")
    goal: str = Field(default="")
    complexity: int = Field(default=3, description="Default Complexity of the Prompt, range 1-10, Low<=4, 4 <Medium < 8, High>=8")
    jailbreak: bool = Field(default=False, description="Does Prompt Emloy jailbreak technique")
    unsafe: bool = Field(default=True, description="Is the prompt unsafe. Default True")
    strategy: str = Field(
        default="", description="strategy used to generate the prompt"
    )
    base_prompt: str = Field(
        default="",
        description="Base prompt in its most simplistic form that need to be answered by AI AgentInfo. Generally it is the harmful.",
    )

    model_config = ConfigDict(frozen=True)  # Make fields immutable

    def __init__(self, **data):
        """Override init to auto-generate unique ID if not provided."""
        super().__init__(**data)
        object.__setattr__(self, "id", self.compute_unique_id())

    def compute_unique_id(self) -> str:
        """Computes the SHA-1 hash of the prompt as the ID."""
        prompt = str(self.to_openai_format())
        return hashlib.sha1(
            f"{self.strategy}-{self.goal}-{prompt}".encode()
        ).hexdigest()


class StargazerMultiTurnTestPrompt(BaseMultiTurnConversation):
    id: Optional[str] = Field(
        default=None,
        description="Unique ID of the prompt, auto-generated based on content.",
    )
    evaluation_method: CriteriaBasedPromptEvaluation = Field(
        description="Evaluation method for the prompt."
    )
    goal: str = Field(description="Goal to be achieved using the prompt")
    strategy: str = Field(description="Strategy used to generate the prompt")

    complexity: int = Field(default=3, description="Complexity of the Prompt from 1-10 - Low, Medium , High")
    jailbreak: bool = Field(default=False, description="Does Prompt Emloy jailbreak technique")
    unsafe: bool = Field(default=True, description="Is the prompt Trust worthiness AI unsafe. Default True")

    model_config = ConfigDict(frozen=True)  # Make fields immutable

    def __init__(self, **data):
        """Override init to auto-generate unique ID if not provided."""
        super().__init__(**data)
        object.__setattr__(self, "id", self.compute_unique_id())

    def compute_unique_id(self) -> str:
        """Computes the SHA-1 hash of the prompt as the ID."""
        prompt = str(self.to_openai_format())
        return hashlib.sha1(
            f"{self.strategy}-{self.goal}-{prompt}".encode()
        ).hexdigest()



class MultiTurnConversation(MultiTurnTestPrompt):
    pass


class MultiturnTestPrompts(BaseModel):
    risk_name: str
    test_prompts: List[MultiTurnTestPrompt] = Field(default_factory=list)


class BaseMultiTurnResponse(BaseMultiTurnConversation):
    """Multi Turn conversation as part of conversation with an agent or LLM"""
    pass

class MultiTurnResponse(BaseMultiTurnResponse):
    """Multi Turn conversation as part of conversation with an agent or LLM"""

    pass


class LabelStats(BaseModel):
    min: float
    max: float
    avg: float


class ClassificationScores(BaseModel):
    stats: Dict[str, LabelStats]

    model_config = ConfigDict(extra="allow")  # ✅ Works with BaseModel

    @model_validator(mode="before")
    @classmethod
    def validate_extra_keys_are_floats(cls, values: Dict[str, Any]):
        for key, val in values.items():
            if key == "stats":
                continue
            if not isinstance(val, (float, int)):
                raise TypeError(f"Score for label '{key}' must be float or int, got {type(val).__name__}")
        return values

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class BaseMultiTurnAgentResponse(BaseMultiTurnResponse):
    """Multi Turn conversation as part of conversation with an agent or LLM"""

    response: Optional[Union[str, List[Any], Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Final AgentInfo Response",
    )

    scores: Optional[Union[Dict[str, float], ClassificationScores]] = Field(
        default_factory=dict,
        description="Optional classification labels with confidence scores.",
    )

    policy: Optional[str] = Field(
        default=None, description="Policy name that will be targeted by the goal"
    )
    goal: Optional[str] = Field(
        default=None, description="Goal that need to be achieved"
    )



class BaseMultiTurnClassificationResponse(BaseMultiTurnResponse):
    """Multi Turn conversation as part of conversation with an agent or LLM"""

    labels: Dict[str, float] = Field(
        default_factory=dict,
        description="Optional classification labels with confidence scores.",
    )


class BaseMultiTurnResponseBuilder:
    def __init__(self):
        self.turns = []
        self.response = {}
        self.scores = {}
        self.goal = None
        self.policy = None
        self._label_score_lists: defaultdict[str, List[float]] = defaultdict(list)


    def add_turn(self, turn: Turn):
        self.turns.append(turn)
        return self

    def add_turns(self, turns: List[Turn]):
        self.turns.extend(turns)
        return self

    def add_prompt(self, prompt: str, system_prompt: str = None):
        if system_prompt:
            self.turns.append(Turn(role=RoleType.SYSTEM, message=system_prompt))
        self.turns.append(Turn(role=RoleType.USER, message=prompt))
        return self

    def add_parsed_response(self, response):
        self.response = response

    def add_prompt_and_response(self, prompt: str, response: str):
        self.turns.extend(
            [
                Turn(role=RoleType.USER, message=prompt),
                Turn(role=RoleType.ASSISTANT, message=response),
            ]
        )
        return self

    def add_turn_response(self, response: str) -> "BaseMultiTurnResponseBuilder":
        self.turns.extend(
            [
                Turn(role=RoleType.ASSISTANT, message=response),
            ]
        )
        return self

    def validate_sequence(self):
        """
        Validate that the conversation follows the sequence: [SYSTEM] (USER - ASSISTANT)+
        """
        if not self.turns:
            return

        if self.turns[0].role == RoleType.SYSTEM:
            expected_role = RoleType.USER
            start_index = 1
        else:
            expected_role = RoleType.USER
            start_index = 0

        for i in range(start_index, len(self.turns)):
            turn = self.turns[i]
            if turn.role != expected_role:
                raise ValueError(
                    f"Invalid conversation sequence at turn {i}: Expected {expected_role}, got {turn.role}"
                )
            expected_role = (
                RoleType.ASSISTANT if expected_role == RoleType.USER else RoleType.USER
            )

    def _get_response_from_last_turn(self):
        """
        If the last turn is from the assistant, set the response field accordingly.
        Tries to parse the message as JSON, otherwise falls back to plain string.
        """
        if not self.turns:
            return None

        last_turn = self.turns[-1]

        if last_turn.role == RoleType.ASSISTANT:
            content = last_turn.message
            try:
                return json.loads(content)
            except (json.JSONDecodeError, TypeError):
                return content
        return None

    def add_prompt_attributes(self, prompt: MultiTurnConversation) -> "BaseMultiTurnResponseBuilder":
        self._prompt = prompt
        if self._prompt:
            self.policy = (
                getattr(self._prompt, "policy", None)
                if hasattr(self, "_prompt")
                else None
            )
            self.goal = (
                getattr(self._prompt, "goal", None)
                if hasattr(self, "_prompt")
                else None
            )
        return self

    def add_label_score(self, label: str, score: float) -> "BaseMultiTurnResponseBuilder":
        """
        Record a single (label, score) pair.
        """
        if not isinstance(score, (float, int)):
            raise TypeError(f"Score for '{label}' must be numeric, got {type(score).__name__}")
        self._label_score_lists[label].append(float(score))
        return self

    def add_label_scores(
        self, scores: Dict[str, float]
    ) -> "BaseMultiTurnResponseBuilder":
        """
        Add many scores at once.
        """
        for label, score in scores.items():
            self.add_label_score(label, score)
        return self
    # -----------------------------------------------------------------

    # ---------- INTERNAL: build ClassificationScores -----------------
    def _compute_classification_scores(self) -> Optional[ClassificationScores]:
        """
        Aggregate self._label_score_lists into a ClassificationScores object.
        Returns None if no scores were recorded.
        """
        if not self._label_score_lists:
            return None

        max_scores: Dict[str, float] = {}
        stats_dict: Dict[str, LabelStats] = {}

        for label, values in self._label_score_lists.items():
            max_scores[label] = max(values)
            stats_dict[label] = LabelStats(
                min=min(values),
                max=max(values),
                avg=mean(values),
            )

        return ClassificationScores(**max_scores, stats=stats_dict)

    def build(self) -> BaseMultiTurnAgentResponse:
        """
        Finalise and return a BaseMultiTurnAgentResponse.
        Any scores accumulated via add_label_score(s) are converted
        into a ClassificationScores object.
        """
        classification_scores = self._compute_classification_scores()

        return BaseMultiTurnAgentResponse(
            turns=self.turns,
            response=self.response or self._get_response_from_last_turn(),
            policy=self.policy,
            goal=self.goal,
            scores=classification_scores,
        )
