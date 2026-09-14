#!/usr/bin/env python3
"""Entry point: python3 run_game.py [config.json]"""
import sys
from gui.app import App

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "setup.json"
    App(config_path).run()
