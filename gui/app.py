"""Main tkinter application window."""
from __future__ import annotations
import tkinter as tk
from tkinter import messagebox

from game.engine import GameEngine, MoveResult
from game.board import Board
from game.graph import Graph
from game.state import GameState
from game.config import load_config
from gui.board_view import BoardView


class App:
    def __init__(self, config_path: str = "setup.json"):
        cfg = load_config(config_path)
        graph = Graph(cfg["graph"]["adjacency_matrix"])
        board = Board(graph, cfg["node_distribution"], cfg["edge_distribution"])
        state = GameState(total_turns=cfg["turns"], budget=cfg["budget"])
        self.engine = GameEngine(graph, board, state)

        self.root = tk.Tk()
        self.root.title("Graph Game")
        self.root.configure(bg="#1C1C1C")

        self._build_hud()
        self.view = BoardView(self.root, self.engine, on_move_callback=self._handle_click)
        self._build_controls()
        self._update_hud()
        self._show_message("Turn 1 — click any node to place yourself.")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_hud(self):
        hud = tk.Frame(self.root, bg="#1C1C1C")
        hud.pack(side="top", fill="x", padx=10, pady=(8, 0))

        def label(text, var, col):
            tk.Label(hud, text=text, bg="#1C1C1C", fg="#AAAAAA",
                     font=("Helvetica", 11)).pack(side="left", padx=(0, 2))
            tk.Label(hud, textvariable=var, bg="#1C1C1C", fg=col,
                     font=("Helvetica", 11, "bold"), width=6).pack(side="left", padx=(0, 16))

        self._var_turn   = tk.StringVar()
        self._var_budget = tk.StringVar()
        self._var_score  = tk.StringVar()
        label("Turn:",   self._var_turn,   "#F9E79F")
        label("Budget:", self._var_budget, "#A9DFBF")
        label("Score:",  self._var_score,  "#AED6F1")

    def _build_controls(self):
        ctrl = tk.Frame(self.root, bg="#1C1C1C")
        ctrl.pack(side="bottom", fill="x", padx=10, pady=8)

        self._msg_var = tk.StringVar()
        tk.Label(ctrl, textvariable=self._msg_var, bg="#1C1C1C", fg="#DDDDDD",
                 font=("Helvetica", 10), wraplength=400).pack(side="left", expand=True)

        tk.Button(ctrl, text="End Turn", command=self._end_turn,
                  bg="#444444", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", padx=12, pady=4).pack(side="right")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _handle_click(self, node: int):
        eng = self.engine
        if eng.state.game_over:
            return

        # Turn 1: place anywhere
        if eng.state.current_node is None:
            if eng.place(node):
                self.view.mark_visited(node)
                self._update_hud()
                self.view.refresh()
                if eng.is_stuck():
                    self._show_message("No affordable moves — end your turn.")
                else:
                    self._show_message(f"Placed on node {node}. Click a green neighbour to move.")
            return

        # Subsequent: try to move
        result = eng.move(node)
        if result == MoveResult.OK:
            self.view.mark_visited(node)
            self._update_hud()
            self.view.refresh()
            if eng.is_stuck():
                self._show_message("No more affordable moves — end your turn.")
            else:
                self._show_message(f"Moved to node {node}. Budget left: {eng.state.budget_remaining}.")
        elif result == MoveResult.INVALID_EDGE:
            self._show_message("No directed edge to that node.")
        elif result == MoveResult.OVER_BUDGET:
            self._show_message("Not enough budget for that edge.")

    def _end_turn(self):
        eng = self.engine
        if eng.state.current_node is None:
            self._show_message("Place yourself on a node first.")
            return
        if eng.state.game_over:
            return

        eng.end_turn()
        self.view.reset_visited()
        self._update_hud()
        self.view.refresh()

        if eng.state.game_over:
            self._show_message(f"Game over!  Final score: {eng.state.total_score}")
            messagebox.showinfo("Game Over",
                                f"Game over!\nFinal score: {eng.state.total_score}")
        else:
            self._show_message(
                f"Turn {eng.state.turn} of {eng.state.total_turns} — "
                f"board redrawn. Budget reset to {eng.state.budget_remaining}."
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_hud(self):
        s = self.engine.state
        self._var_turn.set(f"{s.turn}/{s.total_turns}")
        self._var_budget.set(str(s.budget_remaining))
        self._var_score.set(str(s.total_score))

    def _show_message(self, text: str):
        self._msg_var.set(text)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self):
        self.root.mainloop()
