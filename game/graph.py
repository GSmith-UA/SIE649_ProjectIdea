"""Directed graph built from an adjacency matrix."""
from __future__ import annotations
from collections import deque


class Graph:
    def __init__(self, adjacency_matrix: list[list[int]]):
        self._adj = [list(row) for row in adjacency_matrix]
        self.n = len(self._adj)
        self._validate()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def _validate(self):
        for i, row in enumerate(self._adj):
            if len(row) != self.n:
                raise ValueError(f"Row {i} length {len(row)} != {self.n}")
            if self._adj[i][i] != 0:
                raise ValueError(f"Self-loop at node {i}")
            if all(v == 0 for v in row):
                raise ValueError(f"Node {i} has out-degree zero")
        if not self._is_strongly_connected():
            raise ValueError("Graph is not strongly connected")

    # ------------------------------------------------------------------
    # Reachability (BFS)
    # ------------------------------------------------------------------

    def _reachable(self, src: int, matrix: list[list[int]]) -> set[int]:
        visited = {src}
        queue = deque([src])
        while queue:
            u = queue.popleft()
            for v, has_edge in enumerate(matrix[u]):
                if has_edge and v not in visited:
                    visited.add(v)
                    queue.append(v)
        return visited

    def _is_strongly_connected(self) -> bool:
        if self.n == 0:
            return True
        transpose = [[self._adj[j][i] for j in range(self.n)] for i in range(self.n)]
        forward = self._reachable(0, self._adj)
        backward = self._reachable(0, transpose)
        return len(forward) == self.n and len(backward) == self.n

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def neighbors(self, node: int) -> list[int]:
        """Nodes reachable in one hop from `node`."""
        return [v for v, e in enumerate(self._adj[node]) if e]

    def has_edge(self, u: int, v: int) -> bool:
        return bool(self._adj[u][v])

    def __len__(self) -> int:
        return self.n
