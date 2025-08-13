# python adaptive_solve_planner/worker.py
"""
Worker runner used by ProcessPoolExecutor.

This function is module-level and hence picklable by ProcessPoolExecutor.
"""

from __future__ import annotations

from typing import Dict, Any, Optional
import traceback
import time

from .core import AdaptiveSolverV3


def worker_run_search(init_cfg: Dict[str, Any], seed_args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a solver instance and run a single seed search.

    Returns:
      - plan dict with added '_worker_meta' and '_meta' on success
      - None if search returned no plan for this seed
      - dict with '_error' True and 'trace' if exception occurred
    """
    try:
        solver = AdaptiveSolverV3(
            wc_pct=init_cfg.get("wc_pct", 0.10),
            min_group_size=init_cfg.get("min_group_size", 12),
            max_group_size=init_cfg.get("max_group_size", 20),
            max_adjust_fraction=init_cfg.get("max_adjust_fraction", 0.05),
            max_wc_down_abs=init_cfg.get("max_wc_down_abs", 3),
            max_wc_extra_abs=init_cfg.get("max_wc_extra_abs", 6),
            max_nodes=init_cfg.get("max_nodes", 300000),
            backtrack_depth=init_cfg.get("backtrack_depth", 2),
        )
        solver.time_limit = float(seed_args.get("time_limit", solver.time_limit))

        start = seed_args["start"]
        r0 = seed_args["r0"]
        decay = seed_args["decay"]
        finals = seed_args["finals"]
        rounds = seed_args["rounds"]
        prefer_wc = seed_args["prefer_wc"]
        allow_wc_down = seed_args["allow_wc_down"]
        wc_extra_allow = seed_args["wc_extra_allow"]
        top_k = seed_args["top_k"]
        tol = seed_args["tol"]

        plan = solver._search(start, finals, rounds, r0, decay, prefer_wc, allow_wc_down, wc_extra_allow, top_k, tol)
        if plan is None:
            return None

        plan["_worker_meta"] = {"start": start, "r0": r0, "decay": decay}
        plan["_meta"] = {"time": time.time() - solver.start_time, "nodes": solver.nodes_visited}
        return plan

    except Exception as exc:
        # Return structured error so master process can log or display the traceback.
        return {"_error": True, "trace": traceback.format_exc(), "seed_args": seed_args, "exception": str(exc)}
