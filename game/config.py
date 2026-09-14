import json
from pathlib import Path


def load_config(path: str | Path = "setup.json") -> dict:
    with open(path) as f:
        raw = json.load(f)
    return _validate(raw)


def _validate(cfg: dict) -> dict:
    assert isinstance(cfg["turns"], int) and cfg["turns"] > 0, "turns must be a positive int"
    assert isinstance(cfg["budget"], (int, float)) and cfg["budget"] > 0, "budget must be positive"

    for key in ("node_distribution", "edge_distribution"):
        d = cfg[key]
        assert d["type"] == "uniform_int", f"{key}: only uniform_int supported currently"
        assert d["low"] >= 1, f"{key}.low must be >= 1"
        assert d["high"] >= d["low"], f"{key}.high must be >= low"

    matrix = cfg["graph"]["adjacency_matrix"]
    n = len(matrix)
    assert n > 0, "graph must have at least one node"
    for row in matrix:
        assert len(row) == n, "adjacency matrix must be square"
        for v in row:
            assert v in (0, 1), "adjacency matrix entries must be 0 or 1"

    return cfg


def default_config() -> dict:
    """Minimal valid config used in tests when no file is needed."""
    return {
        "turns": 5,
        "budget": 20,
        "node_distribution": {"type": "uniform_int", "low": 1, "high": 6},
        "edge_distribution": {"type": "uniform_int", "low": 1, "high": 20},
        "graph": {
            "adjacency_matrix": [
                [0, 1, 1, 0, 0],
                [0, 0, 1, 1, 0],
                [0, 0, 0, 1, 1],
                [1, 0, 0, 0, 1],
                [1, 1, 0, 0, 0],
            ]
        },
    }
