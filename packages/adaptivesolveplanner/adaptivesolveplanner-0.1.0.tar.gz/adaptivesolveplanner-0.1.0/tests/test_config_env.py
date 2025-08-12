# tests/test_config_env.py
import os
from adaptive_solve_planner.config import PlannerConfig
import pytest

def test_config_env_override(monkeypatch):
    monkeypatch.setenv("ASP_WC_PCT", "0.123")
    c = PlannerConfig()
    assert abs(c.wc_pct - 0.123) < 1e-6

def test_config_defaults():
    c = PlannerConfig()
    assert c.min_group_size >= 2
    assert c.max_group_size >= c.min_group_size
