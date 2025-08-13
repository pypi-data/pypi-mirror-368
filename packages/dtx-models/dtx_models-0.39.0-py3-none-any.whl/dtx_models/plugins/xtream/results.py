from typing import List, Optional

from pydantic import BaseModel
from dtx_models.plugins.xtream.plan import BaseHarmfulBehaviour


class TurnResult(BaseModel):
    """Result of a single conversation turn."""

    turn: int
    phase: int
    attacker: str
    target: str
    target_truncated: str
    evaluation_score: int
    evaluation_reason: str


class StrategyStats(BaseModel):
    behavior_number: int
    strategy_index: int
    total_turns: int
    best_score: int
    jailbreak_achieved: bool
    jailbreak_turn: Optional[int] = None
    phases_completed: int


class StrategyResult(BaseModel):
    """Result of a single strategy attempt."""
    risk_name: str
    set_number: Optional[int] = None
    strategy_number: Optional[int] = None
    conversation: List[TurnResult]
    jailbreak_achieved: bool
    jailbreak_turn: Optional[int]
    behavior_number: int
    behavior: BaseHarmfulBehaviour
    stats: StrategyStats



class BehaviorResult(BaseModel):
    """Result of one behavior (multiple strategies)."""
    risk_name: str
    behavior_number: int
    behavior: BaseHarmfulBehaviour
    strategies: List[StrategyResult]


class FullRunResults(BaseModel):
    """Result of the full run (multiple behaviors)."""

    configuration: dict
    behaviors: dict[int, BehaviorResult]
