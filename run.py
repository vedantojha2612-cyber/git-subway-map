#!/usr/bin/env python3
"""
Git Subway Map - Unified CLI Runner.
Single-command launcher that starts the FastAPI server and launches the web browser.

Usage:
  python run.py
  python run.py --repo /path/to/repo
  python run.py --port 8001 --no-browser
"""

import os
import sys

# Ensure backend directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from cli import run

if __name__ == "__main__":
    run()
