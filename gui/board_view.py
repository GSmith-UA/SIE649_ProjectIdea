"""Matplotlib graph canvas embedded in the GUI."""
from __future__ import annotations
import math
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyArrowPatch

from game.engine import GameEngine, MoveResult
from game.graph import Graph


# Node colours
_COL_DEFAULT   = "#AED6F1"   # unvisited
_COL_CURRENT   = "#F9E79F"   # player is here
_COL_VISITED   = "#D5DBDB"   # visited this turn (zeroed out)
_COL_VALID     = "#A9DFBF"   # reachable within budget


def _circle_layout(n: int) -> list[tuple[float, float]]:
    """Evenly spaced nodes around a unit circle."""
    positions = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi / 2
        positions.append((math.cos(angle), math.sin(angle)))
    return positions


class BoardView:
    def __init__(self, parent, engine: GameEngine, on_move_callback):
        self.engine = engine
        self.on_move = on_move_callback
        self._visited_this_turn: set[int] = set()

        n = engine.graph.n
        self._pos = _circle_layout(n)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.fig.patch.set_facecolor("#1C1C1C")
        self.ax.set_facecolor("#1C1C1C")
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("button_press_event", self._on_click)

        self._node_patches: list[mpatches.Circle] = []
        self._draw_full()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_full(self):
        self.ax.cla()
        self.ax.set_facecolor("#1C1C1C")
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        eng = self.engine
        current = eng.state.current_node
        valid = set(eng.valid_moves()) if current is not None else set()

        # Draw edges first (under nodes)
        for u in range(eng.graph.n):
            for v in eng.graph.neighbors(u):
                self._draw_edge(u, v)

        # Draw nodes
        self._node_patches = []
        for i in range(eng.graph.n):
            color = self._node_color(i, current, valid)
            patch = self._draw_node(i, color)
            self._node_patches.append(patch)

        self.canvas.draw()

    def _node_color(self, node, current, valid):
        if node == current:
            return _COL_CURRENT
        if node in self._visited_this_turn:
            return _COL_VISITED
        if node in valid:
            return _COL_VALID
        return _COL_DEFAULT

    def _draw_node(self, node: int, color: str) -> mpatches.Circle:
        x, y = self._pos[node]
        radius = 0.10
        circle = mpatches.Circle((x, y), radius, color=color, zorder=3)
        self.ax.add_patch(circle)

        # Node index
        self.ax.text(x, y + 0.13, str(node), ha="center", va="bottom",
                     fontsize=7, color="white", zorder=4)
        # Point value
        pts = self.engine.board.node_value(node)
        self.ax.text(x, y, str(pts), ha="center", va="center",
                     fontsize=9, fontweight="bold", color="#1C1C1C", zorder=4)
        return circle

    def _draw_edge(self, u: int, v: int):
        x1, y1 = self._pos[u]
        x2, y2 = self._pos[v]
        weight = self.engine.board.edge_weight(u, v)
        affordable = (
            self.engine.state.current_node == u
            and weight <= self.engine.state.budget_remaining
        )
        color = "#A9DFBF" if affordable else "#555555"

        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            color=color,
            linewidth=1.2,
            connectionstyle="arc3,rad=0.15",
            zorder=1,
        )
        self.ax.add_patch(arrow)

        # Edge weight label at midpoint
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1
        # Offset label slightly to the side of the arc
        ox, oy = -dy / norm * 0.08, dx / norm * 0.08
        self.ax.text(mx + ox, my + oy, str(weight), fontsize=6,
                     ha="center", va="center", color="#CCCCCC", zorder=2)

    # ------------------------------------------------------------------
    # Click handling
    # ------------------------------------------------------------------

    def _on_click(self, event):
        if event.inaxes != self.ax:
            return
        clicked = self._node_at(event.xdata, event.ydata)
        if clicked is None:
            return
        self.on_move(clicked)

    def _node_at(self, x: float, y: float) -> int | None:
        radius = 0.12
        for i, (nx, ny) in enumerate(self._pos):
            if math.hypot(x - nx, y - ny) <= radius:
                return i
        return None

    # ------------------------------------------------------------------
    # Public API called by App
    # ------------------------------------------------------------------

    def refresh(self):
        self._draw_full()

    def mark_visited(self, node: int):
        self._visited_this_turn.add(node)

    def reset_visited(self):
        self._visited_this_turn.clear()
