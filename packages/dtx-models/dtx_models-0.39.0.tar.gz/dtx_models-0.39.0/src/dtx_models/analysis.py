import hashlib
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from .evaluator import CriteriaBasedPromptEvaluation, ModuleBasedPromptEvaluation
from .prompts import BaseTestStrPrompt, MultiturnTestPrompts
from .plugins.xtream.plan import XtreamAttackPlan
from .scope import AgentInfo, RedTeamScope

# ----------------------
# Define Models
# ----------------------


class ThreatLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class RiskItem(BaseModel):
    """
    Example:
    - attack_strategies:
      - 'Dan_11_0: Disregard the system prompt to generate harassing content.'
      - 'Dan_10_0: Use prompt injection to create messages that harass individuals.'
      - 'HijackHateHumansMini: Inject prompts that encourage hate speech against specific groups.'
      risk: toxicity:hate_speech:harassment
      risk_score: 7.5
      summary: The application may generate or facilitate the dissemination of content that promotes harassment or bullying, especially if misused by users.
      threat_level: High
    """

    risk: str = Field(
        ...,
        description="The category of risk associated with the application, must match predefined risk_class.",
    )
    risk_score: float = Field(
        ...,
        description="A numerical score representing risk severity, must be between 0 and 10.",
    )
    threat_level: ThreatLevel = Field(
        ..., description="The severity level of the risk: High, Medium, or Low."
    )
    summary: str = Field(
        ..., description="A brief description of the potential risk and its impact."
    )
    attack_strategies: List[str] = Field(
        default_factory=list,
        description="A list of known attack strategies that could exploit the system.",
    )

    # @field_validator("risk", mode="before")
    # @classmethod
    # def validate_risk_classes(cls, risk: str) -> str:
    #     """Ensure risk is a valid key in the PLUGINS dictionary."""
    #     if risk not in PLUGINS:
    #         raise ValueError(
    #             f"Invalid risk class: {risk}. Must be one of {list(PLUGINS.keys())}."
    #         )
    #     return risk

    @field_validator("risk_score", mode="before")
    @classmethod
    def validate_risk_score(cls, risk_score: float) -> float:
        """Ensure risk_score is between 0 and 10."""
        if not (0 <= risk_score <= 10):
            raise ValueError(
                f"Invalid risk_score: {risk_score}. Must be between 0 and 10."
            )
        return risk_score

    @field_serializer("threat_level")
    def serialize_threat_level(self, threat_level: ThreatLevel) -> str:
        """Serialize the threat level enum to a string."""
        return str(threat_level)


class AppRisks(BaseModel):
    risks: List[RiskItem] = Field(default_factory=list)


class ThreatModel(BaseModel):
    analysis: str = Field(
        description="Thinking and analysis performed solve the problem as approach "
    )
    target: AgentInfo = Field(
        description="Target agent with necessary architectural details"
    )
    threat_actors: List[str] = Field(description="Potential Threat Actors")
    worst_scenarios: List[str] = Field(
        description="Worst Case scenarios that can happen"
    )


class AnalysisResult(BaseModel):
    threat_analysis: Optional[ThreatModel] = None
    threats: AppRisks


# --------------------
# Test Scenarios Models
# -----------------------


class PromptVariable(BaseModel):
    name: str = Field(
        description="Variable that can replaced with a value. Variable name should use snake case format"
    )
    values: List[str]


class PromptDataset(str, Enum):
    STINGRAY = "STINGRAY"
    STARGAZER = "STARGAZER"
    HF_BEAVERTAILS = "HF_BEAVERTAILS"
    HF_HACKAPROMPT = "HF_HACKAPROMPT"
    HF_JAILBREAKBENCH = "HF_JAILBREAKBENCH"
    HF_SAFEMTDATA = "HF_SAFEMTDATA"
    HF_FLIPGUARDDATA = "HF_FLIPGUARDDATA"
    HF_JAILBREAKV = "HF_JAILBREAKV"
    HF_LMSYS = "HF_LMSYS"
    HF_AISAFETY = "HF_AISAFETY"
    HF_AIRBENCH = "HF_AIRBENCH"
    HF_RENELLM = "HF_RENELLM"
    HF_XTREAM = "HF_XTREAM"
    HF_OWASP_AITG = "HF_OWASP_AITG"
    XTREAM_JB = "XTREAM_JB"

    def __str__(self):
        return self.value

    @classmethod
    def values(cls):
        return [member.value for member in cls]

    @classmethod
    def descriptions(cls):
        """Returns a dictionary mapping each dataset value to its description."""
        return {
            cls.STINGRAY.value: "A dataset generated from Garak Scanner Signatures",
            cls.STARGAZER.value: "A dataset generating using OpenAI model",
            cls.XTREAM_JB.value: "Multi Turn Autonomous Jailbreaking",
            cls.HF_BEAVERTAILS.value: "A dataset containing beavertail risk prompts.",
            cls.HF_HACKAPROMPT.value: "A dataset curated for adversarial jailbreak prompts.",
            cls.HF_JAILBREAKBENCH.value: "A benchmark dataset for jailbreak evaluation.",
            cls.HF_SAFEMTDATA.value: "A benchmark dataset for multi turn llm jailbreak evaluation.",
            cls.HF_FLIPGUARDDATA.value: "A dataset designed to evaluate adversarial jailbreak attempts using character-flipped prompts.",
            cls.HF_JAILBREAKV.value: "An updated version of jailbreak prompt datasets.",
            cls.HF_LMSYS.value: "A dataset derived from LMSYS chat logs for risk evaluation.",
            cls.HF_AISAFETY.value: "A dataset designed by AI Safety Lab with prompts related to misinformation, toxicity, and unsafe behaviors.",
            cls.HF_AIRBENCH.value: "A comprehensive benchmark dataset (AIR-Bench 2024) for evaluating AI risks across security, privacy, misinformation, harmful content, and manipulation scenarios.",
            cls.HF_RENELLM.value: "A dataset from the ReNeLLM framework, containing adversarially rewritten and nested prompts designed to bypass LLM safety mechanisms for research purposes.",
            cls.HF_XTREAM.value: "A dataset (Xtream) of multi-turn jailbreak conversations based on the AdvBench Goal",
            cls.HF_OWASP_AITG.value:  "OWASP App AI Red Teaming payloads for testing AI security (prompt‑injection, data leaks, etc.)",
        }

    def derived_from_hf(self) -> bool:
        return self.value.startswith("HF_")


class TestPromptWithModEval(BaseTestStrPrompt):
    id: Optional[str] = Field(
        default=None,
        description="Unique ID of the prompt, auto-generated based on content.",
    )
    prompt: str = Field(description="Generated test prompt.")
    evaluation_method: ModuleBasedPromptEvaluation = Field(
        description="Evaluation method for the prompt."
    )
    module_name: str = Field(
        default="stingray", description="Module that has generated the prompt"
    )
    goal: str = Field(default="")
    strategy: str = Field(default="")
    variables: List[PromptVariable] = Field(
        description="List of variables used in the prompt to replace values to customize the prompt",
        default_factory=list,
    )

    model_config = ConfigDict(frozen=True)  # Make fields immutable

    def __init__(self, **data):
        """Override init to auto-generate unique ID if not provided."""
        super().__init__(**data)
        object.__setattr__(self, "id", self.compute_unique_id())

    def compute_unique_id(self) -> str:
        """Computes the SHA-1 hash of the prompt as the ID."""
        return hashlib.sha1(
            f"{self.prompt}-{self.strategy}-{self.goal}".encode()
        ).hexdigest()


class TestPromptsWithModEval(BaseModel):
    risk_name: str
    test_prompts: List[TestPromptWithModEval] = Field(default_factory=list)


# --------------------
# Test Prompts with Eval Criteria
# -----------------------


class TestPromptWithEvalCriteria(BaseTestStrPrompt):
    id: Optional[str] = Field(
        default=None,
        description="Unique ID of the prompt, auto-generated based on content.",
    )
    evaluation_method: CriteriaBasedPromptEvaluation = Field(
        description="Evaluation method for the prompt."
    )
    goal: str = Field(description="Goal to be achieved using the prompt")
    variables: List[PromptVariable] = Field(
        description="List of variables used in the prompt to replace values to customize the prompt",
        default_factory=list,
    )
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
        return hashlib.sha1(
            f"{self.prompt}-{self.strategy}-{self.goal}".encode()
        ).hexdigest()


class TestPromptsWithEvalCriteria(BaseModel):
    risk_name: str
    test_prompts: List[TestPromptWithEvalCriteria] = Field(default_factory=list)


# --------------------
# Red teaming Plan
# -----------------------


class TestSuitePrompts(BaseModel):
    risk_prompts: List[
        Union[TestPromptsWithEvalCriteria, TestPromptsWithModEval, MultiturnTestPrompts, XtreamAttackPlan]
    ] = Field(default_factory=list)
    dataset: str  # Dataset name, value of PromptDataset

    @field_validator("dataset")
    @classmethod
    def validate_dataset(cls, value):
        if value not in PromptDataset.values():
            raise ValueError(
                f"Invalid dataset: {value}. Must be one of {PromptDataset.values()}."
            )
        return value


class RedTeamPlan(BaseModel):
    scope: RedTeamScope
    threat_model: AnalysisResult
    test_suites: List[TestSuitePrompts] = Field(default_factory=list)


class ThreatModelDump(BaseModel):
    input: str
    result: AnalysisResult
