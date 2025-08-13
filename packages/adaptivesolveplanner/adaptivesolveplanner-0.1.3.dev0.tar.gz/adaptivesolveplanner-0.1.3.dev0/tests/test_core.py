# python tests/test_core.py
import pytest
from src.adaptive_solve_planner.core import AdaptiveSolverV3

def test_wc_base_and_limits():
    s = AdaptiveSolverV3()
    assert s._wc_base(100) == max(1, int(round(100 * s.wc_pct)))
    wc_min, wc_max = s._wc_limits(100, allow_extra=2, allow_down=True)
    assert wc_min <= wc_max
