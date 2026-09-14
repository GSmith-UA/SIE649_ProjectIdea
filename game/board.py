"""Board holds the random node values and edge weights, and redraws them each turn."""
from __future__ import annotations
import random
from game.graph import Graph


class Board:
    def __init__(self, graph: Graph, node_dist: dict, edge_dist: dict, rng: random.Random | None = None):
        self.graph = graph
        self._node_dist = node_dist
        self._edge_dist = edge_dist
        self._rng = rng or random.Random()

        self.node_values: list[int] = []
        self.edge_weights: dict[tuple[int, int], int] = {}
        self.redraw()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self, dist: dict) -> int:
        assert dist["type"] == "uniform_int"
        return self._rng.randint(dist["low"], dist["high"])

    def redraw(self):
        """Redraw all node values and edge weights from their distributions."""
        n = self.graph.n
        self.node_values = [self._draw(self._node_dist) for _ in range(n)]
        self.edge_weights = {
            (u, v): self._draw(self._edge_dist)
            for u in range(n)
            for v in self.graph.neighbors(u)
        }

    # ------------------------------------------------------------------
    # In-turn mutations
    # ------------------------------------------------------------------

    def collect(self, node: int) -> int:
        """Collect and zero out the value at `node`; return collected amount."""
        pts = self.node_values[node]
        self.node_values[node] = 0
        return pts

    def edge_weight(self, u: int, v: int) -> int:
        return self.edge_weights[(u, v)]

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def node_value(self, node: int) -> int:
        return self.node_values[node]
