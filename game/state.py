from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class GameState:
    total_turns: int
    budget: float

    current_node: int | None = None   # None before the first placement
    turn: int = 1
    budget_remaining: float = field(init=False)
    total_score: int = 0
    game_over: bool = False

    def __post_init__(self):
        self.budget_remaining = self.budget

    def reset_budget(self):
        self.budget_remaining = self.budget

    def advance_turn(self):
        if self.turn >= self.total_turns:
            self.game_over = True
        else:
            self.turn += 1
            self.reset_budget()
