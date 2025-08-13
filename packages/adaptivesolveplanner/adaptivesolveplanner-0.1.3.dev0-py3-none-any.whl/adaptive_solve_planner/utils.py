# python adaptive_solve_planner/utils.py
"""Small utility helpers used across the package."""

from typing import Iterable


def frange(a: float, b: float, step: float) -> Iterable[float]:
    """Float range inclusive of endpoint (small epsilon)."""
    x = a
    while x <= b + 1e-9:
        yield round(x, 6)
        x += step


def ceil_div(a: int, b: int) -> int:
    """Ceiling integer division."""
    return -(-a // b)
