# python adaptive_solve_planner/tools.py
"""Utilities and small CLI helpers used during development.

This file exposes `check_main` used by the poetry-script entrypoint to run
ruff, mypy and pytest in a cross-platform manner.
"""
from __future__ import annotations
import subprocess
import sys
from typing import Sequence


def _run(cmd: Sequence[str]) -> int:
    print("Running:", " ".join(cmd))
    return subprocess.run(list(cmd)).returncode


def check_main() -> None:
    """Run linters and tests (used by `poetry run asp-check`)."""
    rc = _run([sys.executable, "-m", "pytest", "-q"])
    if rc != 0:
        raise SystemExit(rc)
    rc = _run([sys.executable, "-m", "mypy", "adaptive_solve_planner"])
    if rc != 0:
        raise SystemExit(rc)
    rc = _run([sys.executable, "-m", "ruff", "check", "."])
    if rc != 0:
        raise SystemExit(rc)
