# tests/test_api.py
import os
from adaptive_solve_planner.api import plan, parallel_plan

def test_plan_small():
    p = plan(start_guess=100, finals_target=12, rounds_desired=5, strictness="generous",
             prefer_wc=True, allow_wc_down=True, top_k_per_round=12, max_nodes=300000, time_limit=12.0, tol=0)
    assert isinstance(p, dict)
    assert "rows" in p and isinstance(p["rows"], list)
    assert "final_total" in p and isinstance(p["final_total"], int)
    assert p["final_total"] <= 100
    assert "_meta" in p and "start_used" in p["_meta"]

def test_parallel_quick():
    # small smoke test: use small workers to keep runtime short
    p = parallel_plan(start_guess=100, finals_target=12, rounds_desired=5, strictness="generous",
                      prefer_wc=True, allow_wc_down=True, top_k_per_round=8, max_nodes=50000, time_limit=6.0, max_workers=2)
    assert isinstance(p, dict)
    assert "final_total" in p
