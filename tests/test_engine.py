import random
import pytest
from game.graph import Graph
from game.board import Board
from game.state import GameState
from game.engine import GameEngine, MoveResult
from tests.conftest import MATRIX_5


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_engine(matrix=MATRIX_5, turns=5, budget=50, seed=0):
    g = Graph(matrix)
    rng = random.Random(seed)
    cfg_node = {"type": "uniform_int", "low": 1, "high": 6}
    cfg_edge = {"type": "uniform_int", "low": 1, "high": 20}
    b = Board(g, cfg_node, cfg_edge, rng=rng)
    s = GameState(total_turns=turns, budget=budget)
    return GameEngine(g, b, s)


# ---------------------------------------------------------------------------
# Turn 1 placement
# ---------------------------------------------------------------------------

def test_place_any_node_on_turn1():
    eng = make_engine()
    assert eng.state.current_node is None
    assert eng.place(3)
    assert eng.state.current_node == 3


def test_place_twice_fails():
    eng = make_engine()
    eng.place(0)
    assert not eng.place(2)
    assert eng.state.current_node == 0


def test_place_collects_points():
    eng = make_engine()
    eng.board.node_values[2] = 5
    eng.place(2)
    assert eng.state.total_score == 5
    assert eng.board.node_value(2) == 0


# ---------------------------------------------------------------------------
# Budget positivity
# ---------------------------------------------------------------------------

def test_budget_never_goes_negative():
    eng = make_engine(budget=100)
    eng.place(0)
    # Walk as many steps as possible
    for _ in range(200):
        moves = eng.valid_moves()
        if not moves:
            break
        eng.move(moves[0])
    assert eng.state.budget_remaining >= 0


def test_over_budget_move_rejected():
    eng = make_engine(budget=0)  # budget resets to 0 — no move affordable
    eng.place(0)
    result = eng.move(eng.graph.neighbors(0)[0])
    assert result == MoveResult.OVER_BUDGET
    assert eng.state.budget_remaining == 0


# ---------------------------------------------------------------------------
# Valid edge enforcement
# ---------------------------------------------------------------------------

def test_invalid_edge_rejected():
    eng = make_engine()
    eng.place(0)
    # Find a node that is NOT a neighbor of 0
    non_neighbor = next(v for v in range(eng.graph.n) if not eng.graph.has_edge(0, v) and v != 0)
    result = eng.move(non_neighbor)
    assert result == MoveResult.INVALID_EDGE


def test_valid_move_accepted():
    eng = make_engine(budget=100)
    eng.place(0)
    neighbor = eng.graph.neighbors(0)[0]
    result = eng.move(neighbor)
    assert result == MoveResult.OK
    assert eng.state.current_node == neighbor


# ---------------------------------------------------------------------------
# Turn counter terminates at N
# ---------------------------------------------------------------------------

def test_turn_counter_terminates():
    N = 4
    eng = make_engine(turns=N, budget=100)
    eng.place(0)
    for _ in range(N):
        eng.end_turn()
    assert eng.state.game_over


def test_no_moves_after_game_over():
    eng = make_engine(turns=1)
    eng.place(0)
    eng.end_turn()
    assert eng.state.game_over
    neighbor = eng.graph.neighbors(0)[0]
    assert eng.move(neighbor) == MoveResult.GAME_OVER


# ---------------------------------------------------------------------------
# Score accrual
# ---------------------------------------------------------------------------

def test_score_accumulates_across_moves():
    eng = make_engine(budget=200)
    eng.board.node_values = [10] * eng.graph.n  # force known values
    eng.place(0)
    score_after_place = eng.state.total_score
    assert score_after_place == 10

    neighbor = eng.graph.neighbors(0)[0]
    eng.move(neighbor)
    assert eng.state.total_score == 20  # collected two nodes


def test_node_zeroes_out_on_revisit():
    eng = make_engine(budget=200)
    eng.board.node_values = [5] * eng.graph.n
    eng.place(0)
    # Force edge weights to 1 so we can traverse cheaply
    for key in eng.board.edge_weights:
        eng.board.edge_weights[key] = 1

    n1 = eng.graph.neighbors(0)[0]
    eng.move(n1)
    score_before = eng.state.total_score

    # Find a path back to n1 if possible; otherwise just check zero
    assert eng.board.node_value(n1) == 0


# ---------------------------------------------------------------------------
# Budget resets each turn
# ---------------------------------------------------------------------------

def test_budget_resets_on_end_turn():
    eng = make_engine(budget=50, turns=3)
    eng.place(0)
    # Spend some budget
    for key in eng.board.edge_weights:
        eng.board.edge_weights[key] = 1
    neighbor = eng.graph.neighbors(0)[0]
    eng.move(neighbor)
    spent = 50 - eng.state.budget_remaining
    assert spent > 0
    eng.end_turn()
    assert eng.state.budget_remaining == 50


# ---------------------------------------------------------------------------
# is_stuck / valid_moves
# ---------------------------------------------------------------------------

def test_is_stuck_when_budget_zero():
    eng = make_engine(budget=0)
    eng.place(0)
    assert eng.is_stuck()


def test_valid_moves_subset_of_neighbors(graph5):
    eng = make_engine(budget=5)
    eng.place(0)
    vm = eng.valid_moves()
    for v in vm:
        assert eng.graph.has_edge(0, v)
        assert eng.board.edge_weight(0, v) <= 5
