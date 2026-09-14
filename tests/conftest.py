import pytest
import random
from game.graph import Graph
from game.board import Board
from game.config import default_config


# ---------------------------------------------------------------------------
# Test graphs — all directed, strongly connected, no self-loops, out-deg >= 1
# ---------------------------------------------------------------------------

# 5-node ring with a few shortcuts
MATRIX_5 = [
    [0, 1, 0, 0, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0],
]

# 4-node complete directed graph (all pairs, no self-loops)
MATRIX_4_COMPLETE = [
    [0, 1, 1, 1],
    [1, 0, 1, 1],
    [1, 1, 0, 1],
    [1, 1, 1, 0],
]

# 6-node graph: two 3-cycles cross-linked so the whole thing is strongly connected
MATRIX_6 = [
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 0],  # back to 0 AND bridge to 3
    [0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 1, 1, 0, 0],  # back to 2 AND 3
]


@pytest.fixture
def graph5():
    return Graph(MATRIX_5)


@pytest.fixture
def graph4():
    return Graph(MATRIX_4_COMPLETE)


@pytest.fixture
def graph6():
    return Graph(MATRIX_6)


@pytest.fixture
def seeded_rng():
    return random.Random(42)


@pytest.fixture
def cfg():
    return default_config()


@pytest.fixture
def board5(graph5, seeded_rng, cfg):
    return Board(graph5, cfg["node_distribution"], cfg["edge_distribution"], rng=seeded_rng)
