import pytest
from game.graph import Graph
from tests.conftest import MATRIX_5, MATRIX_4_COMPLETE, MATRIX_6


# ---------------------------------------------------------------------------
# Valid graphs construct without error
# ---------------------------------------------------------------------------

def test_graph5_constructs(graph5):
    assert len(graph5) == 5


def test_graph4_constructs(graph4):
    assert len(graph4) == 4


def test_graph6_constructs(graph6):
    assert len(graph6) == 6


# ---------------------------------------------------------------------------
# Strong connectivity
# ---------------------------------------------------------------------------

def test_all_test_graphs_strongly_connected(graph5, graph4, graph6):
    # If construction succeeds, strong connectivity was checked in __init__
    for g in (graph5, graph4, graph6):
        # Every node must reach every other node
        for src in range(g.n):
            reachable = set()
            stack = [src]
            while stack:
                u = stack.pop()
                if u in reachable:
                    continue
                reachable.add(u)
                stack.extend(g.neighbors(u))
            assert reachable == set(range(g.n)), f"Node {src} cannot reach all others"


def test_not_strongly_connected_raises():
    # Two separate cycles — no way to get from 0->2 without crossing from 2->0 only
    broken = [
        [0, 1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ]
    with pytest.raises(ValueError, match="strongly connected"):
        Graph(broken)


# ---------------------------------------------------------------------------
# No self-loops
# ---------------------------------------------------------------------------

def test_self_loop_raises():
    m = [
        [1, 1, 0],
        [0, 0, 1],
        [1, 0, 0],
    ]
    with pytest.raises(ValueError, match="Self-loop"):
        Graph(m)


# ---------------------------------------------------------------------------
# No zero-outdegree nodes
# ---------------------------------------------------------------------------

def test_zero_outdegree_raises():
    # Node 2 has no outgoing edges
    m = [
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 0],
    ]
    with pytest.raises(ValueError, match="out-degree zero"):
        Graph(m)


# ---------------------------------------------------------------------------
# Neighbors / has_edge
# ---------------------------------------------------------------------------

def test_neighbors_match_matrix(graph5):
    for u in range(graph5.n):
        expected = [v for v, e in enumerate(MATRIX_5[u]) if e]
        assert graph5.neighbors(u) == expected


def test_has_edge_true(graph4):
    # complete graph — every off-diagonal pair has an edge
    for u in range(graph4.n):
        for v in range(graph4.n):
            if u != v:
                assert graph4.has_edge(u, v)


def test_has_edge_false_diagonal(graph4):
    for u in range(graph4.n):
        assert not graph4.has_edge(u, u)


# ---------------------------------------------------------------------------
# Non-square matrix rejected
# ---------------------------------------------------------------------------

def test_non_square_raises():
    with pytest.raises(ValueError):
        Graph([[0, 1], [1, 0, 0]])
