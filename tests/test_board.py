import random
from game.board import Board
from game.graph import Graph
from tests.conftest import MATRIX_5


# ---------------------------------------------------------------------------
# Draw bounds
# ---------------------------------------------------------------------------

def test_node_values_in_range(board5, cfg):
    lo, hi = cfg["node_distribution"]["low"], cfg["node_distribution"]["high"]
    for v in board5.node_values:
        assert lo <= v <= hi


def test_edge_weights_in_range(board5, cfg):
    lo, hi = cfg["edge_distribution"]["low"], cfg["edge_distribution"]["high"]
    for w in board5.edge_weights.values():
        assert lo <= w <= hi


def test_only_existing_edges_have_weights(board5, graph5):
    for (u, v) in board5.edge_weights:
        assert graph5.has_edge(u, v)


def test_all_existing_edges_have_weights(board5, graph5):
    for u in range(graph5.n):
        for v in graph5.neighbors(u):
            assert (u, v) in board5.edge_weights


# ---------------------------------------------------------------------------
# Redraw after turn
# ---------------------------------------------------------------------------

def test_redraw_replaces_values(cfg):
    rng = random.Random(0)
    g = Graph(MATRIX_5)
    b = Board(g, cfg["node_distribution"], cfg["edge_distribution"], rng=rng)
    before_nodes = list(b.node_values)
    before_edges = dict(b.edge_weights)
    b.redraw()
    # With a seeded RNG the new draws are deterministic and very likely differ
    assert b.node_values != before_nodes or b.edge_weights != before_edges


def test_redraw_values_still_in_range(board5, cfg):
    lo_n, hi_n = cfg["node_distribution"]["low"], cfg["node_distribution"]["high"]
    lo_e, hi_e = cfg["edge_distribution"]["low"], cfg["edge_distribution"]["high"]
    board5.redraw()
    for v in board5.node_values:
        assert lo_n <= v <= hi_n
    for w in board5.edge_weights.values():
        assert lo_e <= w <= hi_e


# ---------------------------------------------------------------------------
# Collect
# ---------------------------------------------------------------------------

def test_collect_returns_value(board5):
    board5.node_values[0] = 5
    assert board5.collect(0) == 5


def test_collect_zeroes_node(board5):
    board5.node_values[2] = 3
    board5.collect(2)
    assert board5.node_value(2) == 0


def test_collect_zero_node_returns_zero(board5):
    board5.node_values[1] = 0
    assert board5.collect(1) == 0
