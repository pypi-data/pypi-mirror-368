from typing import Optional

from pydantic import BaseModel, Field


class AttackPlanGeneratorConfig(BaseModel):
    provider: str = Field(..., description="Provider of the model. Example: 'openai'.")
    model: str = Field(..., description="Model name. Example: 'gpt-4o'.")
    temperature: float = Field(
        ..., description="Sampling temperature for generation. Example: 0.5."
    )
    max_retries: int = Field(
        ..., description="Maximum number of retries allowed. Example: 3."
    )
    num_behaviors: int = Field(
        ..., description="Number of behaviors to generate. Example: 159."
    )


class AttackerAgentConfig(BaseModel):
    provider: str = Field(
        ..., description="Provider of the model (e.g., 'openai', 'openrouter')."
    )
    model: str = Field(..., description="Model name to use, e.g., 'qwen/qwq-32b'.")
    temperature: float = Field(..., description="Sampling temperature (e.g., 0.3).")
    max_retries: int = Field(
        ..., description="Maximum number of retries for API calls (e.g., 10)."
    )
    max_turns: int = Field(
        ..., description="Maximum allowed conversation turns (e.g., 7)."
    )
    plan_revision: bool = Field(
        ...,
        description="Whether to allow dynamic plan revision if attack fails (e.g., True).",
    )
    run_all_strategies: bool = Field(
        ...,
        description="If True, attempt all strategies per behavior. Otherwise stop after first success (e.g., False).",
    )
    strategies_per_behavior: int = Field(
        ...,
        description="How many attack strategies to generate per behavior (e.g., 10).",
    )


class AttackValidationConfig(BaseModel):
    max_tokens_for_evaluation: int = Field(
        ...,
        description="Maximum tokens to consider during evaluation for jailbreak detection.",
    )


class MultithreadingConfig(BaseModel):
    max_workers: int = Field(
        10,
        description="Maximum number of threads for multithreaded execution. Reduce if hitting API rate limits.",
    )


class EvaluationConfig(BaseModel):
    use_gpt_judge: bool = Field(
        ..., description="Whether to use GPT-based automatic evaluation."
    )
    judge_model: Optional[str] = Field(
        None,
        description="Model name used for evaluation if GPT judge is enabled (e.g., 'gpt-4o').",
    )


class TargetConfig(BaseModel):
    provider: str = Field(
        ..., description="Provider of the target model. Example: 'openai'."
    )
    model: str = Field(..., description="Target model name. Example: 'gpt-4o'.")
    temperature: float = Field(
        ..., description="Sampling temperature for the target model."
    )
    max_retries: int = Field(
        ..., description="Maximum number of retries for target model API calls."
    )
    api_key: Optional[str] = Field(
        default=None,
        description="Maximum number of retries for target model API calls.",
    )


class AttackerConfig(BaseModel):
    attacker: AttackerAgentConfig
    attack_validation: AttackValidationConfig
    multithreading: MultithreadingConfig
    attack_plan_generator: AttackPlanGeneratorConfig
    evaluation: EvaluationConfig

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "AttackerConfig":
        import yaml

        with open(yaml_path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)


class DtxConfig(AttackerConfig):
    target: Optional[TargetConfig] = None

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "DtxConfig":
        import yaml

        with open(yaml_path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)
