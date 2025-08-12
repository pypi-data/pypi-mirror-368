# python adaptive_solve_planner/api.py
"""
API wrappers for AdaptiveSolvePlanner.

Expose two user-facing functions:
 - plan(...)         -> Sequential single-process planning
 - parallel_plan(...) -> Parallel/process-based planning

This module preserves the solver behavior while providing input validation,
auto-tuning (for parallel mode), and coherent metadata in returned plans.

Both `plan` and `parallel_plan` now construct solvers / worker init cfgs using
values from PlannerConfig (environment-overridable) unless overridden by
per-call parameters.
"""

from __future__ import annotations

import time
import multiprocessing
import concurrent.futures
from typing import List, Tuple, Dict, Any, Optional

from .core import AdaptiveSolverV3
from .worker import worker_run_search
from .autotune import auto_tune_for_parallel
from .utils import frange
from .config import PlannerConfig

# Note: safety constants are derived from PlannerConfig defaults if needed.
# Keep module-level fallback constants for quick validation.
FALLBACK_MIN_START = 2
FALLBACK_MAX_START = 10000
FALLBACK_MIN_ROUNDS = 2
FALLBACK_MAX_ROUNDS = 16


def _validate_inputs(start_guess: int, finals_target: int, rounds_desired: int, cfg: PlannerConfig) -> None:
    """Validate common input bounds for the public API using PlannerConfig limits."""
    min_rounds = cfg.min_rounds or FALLBACK_MIN_ROUNDS
    max_rounds = cfg.max_rounds or FALLBACK_MAX_ROUNDS
    if rounds_desired < min_rounds or rounds_desired > max_rounds:
        raise ValueError(f"rounds_desired must be between {min_rounds} and {max_rounds}")
    if start_guess < finals_target:
        raise ValueError("start_guess must be >= finals_target")
    min_start = cfg.min_start or FALLBACK_MIN_START
    max_start = cfg.max_start or FALLBACK_MAX_START
    if start_guess < min_start or start_guess > max_start:
        raise ValueError(f"start_guess must be between {min_start} and {max_start}")


def plan(
    start_guess: int,
    finals_target: int,
    rounds_desired: int,
    strictness: str = "moderate",
    prefer_wc: bool = True,
    allow_wc_down: bool = True,
    allow_start_adjust: bool = False,
    start_adjust_range: int = 3,
    r0_delta_pct: float = 0.05,
    decay_values: Optional[List[float]] = None,
    wc_extra_try: int = 4,
    top_k_per_round: int = 12,
    max_nodes: int = 300000,
    time_limit: float = 12.0,
    tol: int = 0,
    cfg: Optional[PlannerConfig] = None,
) -> Dict[str, Any]:
    """
    Sequential planner (single-process).

    The PlannerConfig instance (if provided) or environment-configured PlannerConfig
    is used to build the solver defaults (group sizes, wildcard defaults, etc).
    """
    cfg = cfg or PlannerConfig()
    _validate_inputs(start_guess, finals_target, rounds_desired, cfg)

    strict_map = {"generous": 0.70, "moderate": 0.60, "stringent": 0.50}
    if strictness not in strict_map:
        raise ValueError("strictness must be 'generous','moderate' or 'stringent'")

    r0_base = strict_map[strictness]

    deltas = [0.0, -r0_delta_pct, -r0_delta_pct / 2.0, r0_delta_pct / 2.0, r0_delta_pct]
    if decay_values is None:
        decay_values = [round(x, 4) for x in frange(0.60, 0.95, 0.035)]

    starts = [start_guess]
    if allow_start_adjust:
        for s in range(max(finals_target, start_guess - start_adjust_range), start_guess + start_adjust_range + 1):
            if s not in starts:
                starts.append(s)

    combos: List[Tuple[int, float, float]] = []
    for s in starts:
        for delta in deltas:
            r0 = max(0.01, min(0.99, r0_base * (1.0 + delta)))
            for decay in decay_values:
                combos.append((s, r0, decay))

    # Build solver using PlannerConfig -> ensures all solver defaults come from config
    solver = AdaptiveSolverV3(
        wc_pct=cfg.wc_pct,
        min_group_size=cfg.min_group_size,
        max_group_size=cfg.max_group_size,
        max_adjust_fraction=cfg.max_adjust_fraction,
        max_wc_down_abs=cfg.max_wc_down_abs,
        max_wc_extra_abs=cfg.max_wc_extra_abs,
        max_nodes=max_nodes or cfg.default_max_nodes,
        backtrack_depth=cfg.backtrack_depth,
    )
    solver.time_limit = time_limit or cfg.default_time_limit

    overall_start = time.time()
    best_plan = None
    best_score = None
    seeds_tried = 0

    for (s, r0, decay) in combos:
        if time.time() - overall_start > (time_limit or cfg.default_time_limit):
            break

        plan_dict = solver._search(
            s,
            finals_target,
            rounds_desired,
            r0,
            decay,
            prefer_wc,
            allow_wc_down,
            wc_extra_try,
            top_k_per_round,
            tol,
        )
        seeds_tried += 1
        if plan_dict is None:
            continue

        final_total = plan_dict["final_total"]
        diff = abs(final_total - finals_target)
        wc_excess = sum(
            max(0, r["wildcards"] - solver._wc_base(r["participants"])) for r in plan_dict["rows"] if r["round"] < rounds_desired
        )
        packing_waste = sum(
            (r["groups"] * r["group_size"] - r["participants"]) for r in plan_dict["rows"] if r["participants"] > 0
        )
        score = (diff, wc_excess, packing_waste, abs(s - start_guess))
        plan_dict["_score"] = score
        plan_dict["_meta"] = {
            "mode": "sequential",
            "start_used": s,
            "r0_used": r0,
            "decay_used": decay,
            "nodes": solver.nodes_visited,
            "time": time.time() - overall_start,
        }
        if best_plan is None or score < best_score:
            best_plan = plan_dict
            best_score = score
        if score[0] == 0 and score[1] == 0 and score[2] == 0:
            break

    if best_plan is None:
        raise RuntimeError("No plan found (sequential)")

    best_plan["_meta"]["seeds_tried"] = seeds_tried
    best_plan["_meta"]["wall_time_total"] = time.time() - overall_start
    best_plan["_meta"]["settings_used"] = {"top_k_per_round": top_k_per_round, "max_nodes": max_nodes, "time_limit": time_limit}
    # include config snapshot for reproducibility
    best_plan["_meta"]["config_snapshot"] = cfg.model_dump()
    return best_plan


def parallel_plan(
    start_guess: int,
    finals_target: int,
    rounds_desired: int,
    strictness: str = "moderate",
    prefer_wc: bool = True,
    allow_wc_down: bool = True,
    allow_start_adjust: bool = False,
    start_adjust_range: int = 3,
    r0_delta_pct: float = 0.05,
    decay_values: Optional[List[float]] = None,
    wc_extra_try: int = 4,
    top_k_per_round: Optional[int] = None,
    max_nodes: Optional[int] = None,
    time_limit: Optional[float] = None,
    tol: int = 0,
    max_workers: Optional[int] = None,
    cfg: Optional[PlannerConfig] = None,
) -> Dict[str, Any]:
    """
    Parallel/process-based planner.

    Uses PlannerConfig for solver defaults and worker init config. When top_k_per_round,
    max_nodes or time_limit are None they will be auto-tuned using the heuristic.
    """
    cfg = cfg or PlannerConfig()
    _validate_inputs(start_guess, finals_target, rounds_desired, cfg)

    strict_map = {"generous": 0.70, "moderate": 0.60, "stringent": 0.50}
    if strictness not in strict_map:
        raise ValueError("strictness must be 'generous','moderate' or 'stringent'")

    r0_base = strict_map[strictness]

    # Auto-tune if user left parallel tuning args as None
    if top_k_per_round is None or max_nodes is None or time_limit is None:
        tune = auto_tune_for_parallel(start_guess, rounds_desired)
        if top_k_per_round is None:
            top_k_per_round = tune["top_k_per_round"]
        if max_nodes is None:
            max_nodes = tune["max_nodes"]
        if time_limit is None:
            time_limit = tune["time_limit"]

    # Clamp chosen values to safe ranges
    top_k_per_round = int(max(3, min(60, int(top_k_per_round))))
    max_nodes = int(max(1000, min(10_000_000, int(max_nodes))))
    time_limit = float(max(1.0, min(3600.0, float(time_limit))))

    deltas = [0.0, -r0_delta_pct, -r0_delta_pct / 2.0, r0_delta_pct / 2.0, r0_delta_pct]
    if decay_values is None:
        decay_values = [round(x, 4) for x in frange(0.60, 0.95, 0.035)]

    starts = [start_guess]
    if allow_start_adjust:
        for s in range(max(finals_target, start_guess - start_adjust_range), start_guess + start_adjust_range + 1):
            if s not in starts:
                starts.append(s)

    combos: List[Tuple[int, float, float]] = []
    for s in starts:
        for delta in deltas:
            r0 = max(0.01, min(0.99, r0_base * (1.0 + delta)))
            for decay in decay_values:
                combos.append((s, r0, decay))

    # Prepare worker init configuration from PlannerConfig
    init_cfg = cfg.to_worker_init_cfg(max_nodes_override=max_nodes)

    seeds = []
    for (s, r0, decay) in combos:
        seeds.append(
            {
                "start": s,
                "r0": r0,
                "decay": decay,
                "finals": finals_target,
                "rounds": rounds_desired,
                "prefer_wc": prefer_wc,
                "allow_wc_down": allow_wc_down,
                "wc_extra_allow": wc_extra_try,
                "top_k": top_k_per_round,
                "tol": tol,
                "time_limit": time_limit,
            }
        )

    cpu_count = multiprocessing.cpu_count() or 2
    if max_workers is None:
        max_workers = min(cpu_count, len(seeds))
    else:
        max_workers = min(int(max_workers), cpu_count, len(seeds))

    wall_start = time.time()
    best_plan = None
    best_score = None

    # Submit seeds to worker pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker_run_search, init_cfg, seed) for seed in seeds]
        for fut in concurrent.futures.as_completed(futures, timeout=None):
            try:
                res = fut.result()
            except Exception as e:
                print("[worker crashed]", e)
                continue

            if res is None:
                continue
            if isinstance(res, dict) and res.get("_error"):
                print("[worker error trace]\n", res.get("trace", "<no trace>"))
                continue

            plan = res
            final_total = plan["final_total"]
            diff = abs(final_total - finals_target)
            wc_excess = sum(
                max(0, r["wildcards"] - AdaptiveSolverV3(wc_pct=cfg.wc_pct)._wc_base(r["participants"])) for r in plan["rows"] if r["round"] < rounds_desired
            )
            packing_waste = sum((r["groups"] * r["group_size"] - r["participants"]) for r in plan["rows"] if r["participants"] > 0)
            score = (diff, wc_excess, packing_waste, abs(plan.get("_worker_meta", {}).get("start", start_guess) - start_guess))
            plan["_score"] = score
            plan["_meta"] = plan.get("_meta", {})
            plan["_meta"]["worker_meta"] = plan.get("_worker_meta", {})
            plan["_meta"]["collected_at_since_wall_start"] = time.time() - wall_start

            if best_plan is None or score < best_score:
                best_plan = plan
                best_score = score
            if score[0] == 0 and score[1] == 0 and score[2] == 0:
                break

    if best_plan is None:
        raise RuntimeError("No plan found (parallel)")

    total_wall_time = time.time() - wall_start
    best_plan["_meta"]["mode"] = "parallel"
    best_plan["_meta"]["wall_time_total"] = total_wall_time
    best_plan["_meta"]["seeds_tried"] = len(seeds)
    best_plan["_meta"]["cores_used"] = max_workers
    best_plan["_meta"]["settings_used"] = {"top_k_per_round": top_k_per_round, "max_nodes": max_nodes, "time_limit": time_limit}
    best_plan["_meta"]["config_snapshot"] = cfg.model_dump()
    return best_plan
