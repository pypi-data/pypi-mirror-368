# python adaptive_solve_planner/autotune.py
"""
Auto-tuning heuristics for parallel execution.

This module exposes auto_tune_for_parallel(...) which computes sensible values
for top_k_per_round, max_nodes and time_limit based on `start` and `rounds`.
"""

from __future__ import annotations
from typing import Dict


def auto_tune_for_parallel(start: int, rounds: int) -> Dict[str, int]:
    """
    Heuristic auto-tuner for parallel mode.

    Returns tuned top_k_per_round, max_nodes and time_limit (seconds).
    Anchor: start=100, rounds=5 -> top_k~12, max_nodes~300000, time_limit~12.
    """
    anchor_start = 100.0
    anchor_rounds = 5.0

    s = max(2.0, float(start))
    r = max(2.0, float(rounds))

    top_k = int(round(12.0 * (s / anchor_start) ** 0.25 * (r / anchor_rounds) ** 0.35))
    top_k = max(6, min(60, top_k))

    max_nodes = int(round(300000 * (s / anchor_start) ** 0.8 * (r / anchor_rounds) ** 1.6))
    max_nodes = max(50000, min(10_000_000, max_nodes))

    time_limit = int(round(12.0 * (s / anchor_start) ** 0.5 * (r / anchor_rounds) ** 1.2))
    time_limit = max(6, min(3600, time_limit))

    return {"top_k_per_round": top_k, "max_nodes": max_nodes, "time_limit": time_limit}
