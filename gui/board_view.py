"""Matplotlib graph canvas embedded in the GUI."""
from __future__ import annotations
import math
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from game.engine import GameEngine


_COL_DEFAULT = "#AED6F1"   # unvisited
_COL_CURRENT = "#F9E79F"   # player is here
_COL_VISITED = "#D5DBDB"   # collected this turn (zeroed out)
_COL_VALID   = "#A9DFBF"   # reachable within budget

_NODE_R      = 0.13        # node circle radius in data coords
_PAD         = 0.35        # axis padding beyond the unit circle
_SHRINK_PTS  = 22          # arrow shrink from node centre (display points)


def _circle_layout(n: int) -> list[tuple[float, float]]:
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

        self._pos = _circle_layout(engine.graph.n)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.fig.patch.set_facecolor("#1C1C1C")

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("button_press_event", self._on_click)

        self._draw_full()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_full(self):
        self.ax.cla()
        self.ax.set_facecolor("#1C1C1C")
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        # Must set limits explicitly — add_patch() does NOT expand them.
        lim = 1.0 + _PAD
        self.ax.set_xlim(-lim, lim)
        self.ax.set_ylim(-lim, lim)

        eng = self.engine
        current = eng.state.current_node

        # Before first placement: every node is a valid starting square.
        if current is None:
            valid = set(range(eng.graph.n))
        else:
            valid = set(eng.valid_moves())

        for u in range(eng.graph.n):
            for v in eng.graph.neighbors(u):
                self._draw_edge(u, v, current)

        for i in range(eng.graph.n):
            self._draw_node(i, self._node_color(i, current, valid))

        self.canvas.draw()

    def _node_color(self, node, current, valid):
        if node == current:
            return _COL_CURRENT
        if node in self._visited_this_turn:
            return _COL_VISITED
        if node in valid:
            return _COL_VALID
        return _COL_DEFAULT

    def _draw_node(self, node: int, color: str):
        x, y = self._pos[node]
        self.ax.add_patch(mpatches.Circle((x, y), _NODE_R, color=color, zorder=3))
        # Node index label above the circle
        self.ax.text(x, y + _NODE_R + 0.05, str(node),
                     ha="center", va="bottom", fontsize=8, color="white", zorder=5)
        # Current point value inside the circle
        pts = self.engine.board.node_value(node)
        self.ax.text(x, y, str(pts),
                     ha="center", va="center", fontsize=11, fontweight="bold",
                     color="#1C1C1C", zorder=5)

    def _draw_edge(self, u: int, v: int, current):
        x1, y1 = self._pos[u]
        x2, y2 = self._pos[v]
        weight = self.engine.board.edge_weight(u, v)
        affordable = (
            current == u
            and weight <= self.engine.state.budget_remaining
        )
        color = "#A9DFBF" if affordable else "#666666"

        # annotate gives clean shrinkA/B support — arrows start/end at node edges.
        self.ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=1.3,
                mutation_scale=13,
                connectionstyle="arc3,rad=0.18",
                shrinkA=_SHRINK_PTS,
                shrinkB=_SHRINK_PTS,
            ),
            zorder=1,
        )

        # Weight label offset perpendicular to the midpoint
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        norm = math.hypot(dx, dy) or 1
        ox, oy = -dy / norm * 0.14, dx / norm * 0.14
        self.ax.text(mx + ox, my + oy, str(weight),
                     fontsize=7, ha="center", va="center",
                     color="#CCCCCC", zorder=2)

    # ------------------------------------------------------------------
    # Click handling
    # ------------------------------------------------------------------

    def _on_click(self, event):
        if event.inaxes != self.ax:
            return
        node = self._node_at(event.xdata, event.ydata)
        if node is not None:
            self.on_move(node)

    def _node_at(self, x: float, y: float) -> int | None:
        hit_r = _NODE_R + 0.04   # slightly larger than drawn circle
        for i, (nx, ny) in enumerate(self._pos):
            if math.hypot(x - nx, y - ny) <= hit_r:
                return i
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self):
        self._draw_full()

    def mark_visited(self, node: int):
        self._visited_this_turn.add(node)

    def reset_visited(self):
        self._visited_this_turn.clear()
