"""Orchestrates turns: move validation, scoring, end-of-turn redraw."""
from __future__ import annotations
from enum import Enum, auto
from game.board import Board
from game.graph import Graph
from game.state import GameState


class MoveResult(Enum):
    OK = auto()
    INVALID_EDGE = auto()       # no directed edge u->v
    OVER_BUDGET = auto()        # edge weight would exceed remaining budget
    GAME_OVER = auto()          # trying to move when game already ended
    NOT_PLACED = auto()         # trying to move before placing on turn 1


class GameEngine:
    def __init__(self, graph: Graph, board: Board, state: GameState):
        self.graph = graph
        self.board = board
        self.state = state

    # ------------------------------------------------------------------
    # Turn 1 placement
    # ------------------------------------------------------------------

    def place(self, node: int) -> bool:
        """Place the player on any node to begin Turn 1. Returns False if already placed."""
        if self.state.current_node is not None:
            return False
        if not (0 <= node < self.graph.n):
            return False
        self.state.current_node = node
        pts = self.board.collect(node)
        self.state.total_score += pts
        return True

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------

    def move(self, destination: int) -> MoveResult:
        """Attempt to move from current node to `destination`."""
        if self.state.game_over:
            return MoveResult.GAME_OVER
        if self.state.current_node is None:
            return MoveResult.NOT_PLACED

        src = self.state.current_node
        if not self.graph.has_edge(src, destination):
            return MoveResult.INVALID_EDGE

        cost = self.board.edge_weight(src, destination)
        if cost > self.state.budget_remaining:
            return MoveResult.OVER_BUDGET

        self.state.budget_remaining -= cost
        self.state.current_node = destination
        pts = self.board.collect(destination)
        self.state.total_score += pts
        return MoveResult.OK

    # ------------------------------------------------------------------
    # End turn
    # ------------------------------------------------------------------

    def end_turn(self):
        """End the current turn: redraw the board, advance turn counter."""
        self.board.redraw()
        self.state.advance_turn()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def valid_moves(self) -> list[int]:
        """Neighbors reachable within the remaining budget."""
        if self.state.current_node is None or self.state.game_over:
            return []
        src = self.state.current_node
        return [
            v for v in self.graph.neighbors(src)
            if self.board.edge_weight(src, v) <= self.state.budget_remaining
        ]

    def is_stuck(self) -> bool:
        """True when no move is affordable — player must end their turn."""
        return len(self.valid_moves()) == 0
