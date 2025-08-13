# python adaptive_solve_planner/annotated_original.py
#!/usr/bin/env python3
"""
This file is the annotated original AdaptiveSolverV3 script you provided, with
line-by-line comments explaining each statement and reasoning.

Note: This is *read-only* documentation and not used by the runtime package.
"""

from __future__ import annotations  # ensure forward references work for type hints
import math  # math utilities
import time  # for timing and timeouts
import traceback  # to produce stack traces on exceptions
import multiprocessing  # used by parallel mode to find CPU count
from typing import List, Dict, Any, Optional, Tuple  # typing hints
import concurrent.futures  # ProcessPoolExecutor

# ---------------------------
# Limits / defaults
# ---------------------------
MIN_START = 2  # minimum allowed start teams
MAX_START = 10000  # maximum allowed start teams (safeguard)
MIN_ROUNDS = 2  # minimum number of rounds
MAX_ROUNDS = 16  # maximum rounds allowed (safeguard)

# Defaults used when not auto-tuned (sequential)
DEFAULT_SEQ_TOP_K = 12  # default candidate list size
DEFAULT_SEQ_MAX_NODES = 300000  # default node budget
DEFAULT_SEQ_TIME_LIMIT = 12.0  # seconds

# ---------------------------
# Core Solver (original V3 logic preserved)
# ---------------------------
class AdaptiveSolverV3:
    # Preferred qualifiers-per-group and group sizes list
    PREFERRED_QPG = [16,15,14,12,10,8,6,5,4,3]
    PREFERRED_GROUP_SIZES = [20,16,18,12]

    def __init__(self,
                 wc_pct: float = 0.10,
                 min_group_size: int = 12,
                 max_group_size: int = 20,
                 max_adjust_fraction: float = 0.05,
                 max_wc_down_abs: int = 3,
                 max_wc_extra_abs: int = 6,
                 max_nodes: int = 300000,
                 backtrack_depth: int = 2):
        # store configuration parameters passed in
        self.wc_pct = float(wc_pct)
        self.min_g = int(min_group_size)
        self.max_g = int(max_group_size)
        self.max_adjust_fraction = float(max_adjust_fraction)
        self.max_wc_down_abs = int(max_wc_down_abs)
        self.max_wc_extra_abs = int(max_wc_extra_abs)
        self.max_nodes = int(max_nodes)
        self.backtrack_depth = int(backtrack_depth)

        # runtime state initialization
        self.nodes_visited = 0
        self.start_time = 0.0
        self.time_limit = DEFAULT_SEQ_TIME_LIMIT

    def _ceil_div(self,a:int,b:int)->int:
        # a simple ceiling division
        return -(-a//b)

    def _wc_base(self, participants:int)->int:
        # base wildcards computed as rounded percentage of participants
        if participants <= 1:
            return 0
        return max(1, int(round(participants * self.wc_pct)))

    def _wc_limits(self, participants:int, allow_extra:int, allow_down:bool) -> Tuple[int,int]:
        # compute allowed wildcard range
        base = self._wc_base(participants)
        extra = min(self.max_wc_extra_abs, allow_extra)
        down = min(self.max_wc_down_abs if allow_down else 0, int(math.floor(participants * 0.05)))
        wc_min = max(0, base - down)
        wc_max = min(participants - 1, base + extra)
        return wc_min, wc_max

    def _is_preferred_multiple(self, val:int) -> bool:
        # check if val is divisible by any preferred group size
        for s in self.PREFERRED_GROUP_SIZES:
            if s > 0 and val % s == 0:
                return True
        return False

    def _group_candidates(self, participants:int) -> List[int]:
        # compute maximum groups given min group size and return range 1..max_groups
        max_groups = max(1, self._ceil_div(participants, self.min_g))
        return list(range(1, max_groups + 1))

    def _try_round_candidates(self, participants:int, desired_qual:int, prev_qpg:Optional[int],
                              wc_min:int, wc_max:int, prefer_wc:bool, top_k:int=8) -> List[Dict[str,Any]]:
        """Return sorted list (top_k) for the current round (kept scoring as before)."""
        allowed_adj = min(5, max(1, int(self.max_adjust_fraction * participants)))
        candidates = []
        base_wc = self._wc_base(participants)

        for groups in self._group_candidates(participants):
            actual_group_size = self._ceil_div(participants, groups)
            if actual_group_size < self.min_g or actual_group_size > self.max_g:
                continue

            qpgs = [q for q in self.PREFERRED_QPG if q <= actual_group_size]
            if not qpgs:
                qpgs = [max(1, min(actual_group_size, desired_qual // max(1, groups)))]

            for qpg in qpgs:
                if prev_qpg is not None and qpg > prev_qpg:
                    continue
                qualifiers_total = qpg * groups
                if qualifiers_total > participants:
                    continue

                wc_options = list(range(wc_min, wc_max + 1))
                if prefer_wc and base_wc in wc_options:
                    wc_options = [base_wc] + [w for w in wc_options if w != base_wc]

                for wc in wc_options:
                    next_total = qualifiers_total + wc
                    monotonic_pen = 0 if next_total < participants else 100000 + (next_total - participants)
                    nice = 0 if self._is_preferred_multiple(next_total) else 1
                    wc_dev = abs(wc - base_wc)
                    desired_next = desired_qual + base_wc
                    diff_next = abs(desired_next - next_total)
                    remainder = groups * actual_group_size - participants
                    score = (monotonic_pen, nice, diff_next, wc_dev * 10, remainder, groups, -qpg)
                    candidates.append({
                        'groups': groups,
                        'group_size': actual_group_size,
                        'qpg': qpg,
                        'qualifiers_total': qualifiers_total,
                        'wildcards': wc,
                        'next_total': next_total,
                        'score': score
                    })
        candidates.sort(key=lambda c: c['score'])
        return candidates[:top_k]

    def _search(self, start:int, finals:int, rounds:int, r0:float, decay:float,
                prefer_wc:bool, allow_wc_down:bool, wc_extra_allow:int, top_k:int, tol:int) -> Optional[Dict[str,Any]]:
        """DFS/backtracking search. Returns a plan dict or None."""
        self.nodes_visited = 0
        self.start_time = time.time()
        best_plan = None
        best_score = None

        def dfs(round_idx:int, participants:int, prev_qpg:Optional[int], rows:List[Dict[str,Any]]):
            nonlocal best_plan, best_score
            if time.time() - self.start_time > self.time_limit or self.nodes_visited > self.max_nodes:
                return
            self.nodes_visited += 1

            if round_idx == rounds:
                final_total = participants
                diff = abs(final_total - finals)
                wc_excess = sum(max(0, r['wildcards'] - self._wc_base(r['participants'])) for r in rows if r['round'] < rounds)
                packing_waste = sum((r['groups'] * r['group_size'] - r['participants']) for r in rows if r['participants'] > 0)
                score = (diff, wc_excess, packing_waste)
                if best_plan is None or score < best_score:
                    plan = {'rows': [dict(r) for r in rows], 'final_total': final_total, 'score': score}
                    best_plan = plan
                    best_score = score
                return

            raw_r = r0 * (decay ** (round_idx - 1))
            r = min(raw_r, 0.80)
            desired_qual = max(1, int(round(participants * r)))

            wc_min, wc_max = self._wc_limits(participants, wc_extra_allow, allow_wc_down)
            candidates = self._try_round_candidates(participants, desired_qual, prev_qpg, wc_min, wc_max, prefer_wc, top_k=top_k)
            if not candidates:
                return

            for cand in candidates:
                if cand['next_total'] >= participants:
                    continue
                row = {
                    'round': round_idx,
                    'participants': participants,
                    'groups': cand['groups'],
                    'group_size': cand['group_size'],
                    'qualifiers_per_group': cand['qpg'],
                    'qualifiers_total': cand['qualifiers_total'],
                    'wildcards': cand['wildcards'],
                    'next_total': cand['next_total'],
                    'retention': round(r, 6)
                }
                rows.append(row)
                dfs(round_idx + 1, cand['next_total'], cand['qpg'], rows)
                rows.pop()
                if time.time() - self.start_time > self.time_limit or self.nodes_visited > self.max_nodes:
                    return

        dfs(1, start, None, [])
        return best_plan

# ---------------------------
# Worker (top-level, picklable)
# ---------------------------
def worker_run_search(init_cfg: Dict[str,Any], seed_args: Dict[str,Any]) -> Optional[Dict[str,Any]]:
    """
    Recreate a solver in worker process and run a single seed search.
    Returns plan dict (with _worker_meta and _meta) or {'_error': True, 'trace': ...} on exception.
    """
    try:
        solver = AdaptiveSolverV3(
            wc_pct = init_cfg.get('wc_pct', 0.10),
            min_group_size = init_cfg.get('min_group_size', 12),
            max_group_size = init_cfg.get('max_group_size', 20),
            max_adjust_fraction = init_cfg.get('max_adjust_fraction', 0.05),
            max_wc_down_abs = init_cfg.get('max_wc_down_abs', 3),
            max_wc_extra_abs = init_cfg.get('max_wc_extra_abs', 6),
            max_nodes = init_cfg.get('max_nodes', 300000),
            backtrack_depth = init_cfg.get('backtrack_depth', 2)
        )
        solver.time_limit = float(seed_args.get('time_limit', solver.time_limit))

        start = seed_args['start']
        r0 = seed_args['r0']
        decay = seed_args['decay']
        finals = seed_args['finals']
        rounds = seed_args['rounds']
        prefer_wc = seed_args['prefer_wc']
        allow_wc_down = seed_args['allow_wc_down']
        wc_extra_allow = seed_args['wc_extra_allow']
        top_k = seed_args['top_k']
        tol = seed_args['tol']

        plan = solver._search(start, finals, rounds, r0, decay, prefer_wc, allow_wc_down, wc_extra_allow, top_k, tol)
        if plan is None:
            return None

        plan['_worker_meta'] = {'start': start, 'r0': r0, 'decay': decay}
        plan['_meta'] = {'time': time.time() - solver.start_time, 'nodes': solver.nodes_visited}
        return plan

    except Exception:
        return {'_error': True, 'trace': traceback.format_exc(), 'seed_args': seed_args}

# ---------------------------
# Auto-tuner for parallel mode (exponential-ish scaling)
# ---------------------------
def auto_tune_for_parallel(start: int, rounds: int) -> Dict[str,Any]:
    """
    Heuristic: returns dict with keys 'top_k_per_round', 'max_nodes', 'time_limit'.
    Tuned to produce (for start=100, rounds=5): top_k~12, max_nodes~300000, time_limit~12.
    Scaling is monotonic: top_k grows slowly; max_nodes and time_limit grow faster with rounds/start.
    """
    anchor_start = 100.0
    anchor_rounds = 5.0

    s = max(2.0, float(start))
    r = max(2.0, float(rounds))

    # top_k scales slowly
    top_k = int(round(12.0 * (s/anchor_start)**0.25 * (r/anchor_rounds)**0.35))
    top_k = max(6, min(40, top_k))

    # max_nodes scales faster
    max_nodes = int(round(300000 * (s/anchor_start)**0.8 * (r/anchor_rounds)**1.6))
    max_nodes = max(50000, min(5_000_000, max_nodes))

    # time_limit
    time_limit = int(round(12.0 * (s/anchor_start)**0.5 * (r/anchor_rounds)**1.2))
    time_limit = max(6, min(3600, time_limit))

    return {'top_k_per_round': top_k, 'max_nodes': max_nodes, 'time_limit': float(time_limit)}

# ---------------------------
# Two API functions: plan (sequential) and parallel_plan (parallel)
# ---------------------------
def _validate_inputs(start_guess:int, finals_target:int, rounds_desired:int):
    if rounds_desired < MIN_ROUNDS or rounds_desired > MAX_ROUNDS:
        raise ValueError(f"rounds_desired must be between {MIN_ROUNDS} and {MAX_ROUNDS}")
    if start_guess < finals_target:
        raise ValueError("start_guess must be >= finals_target")
    if start_guess < MIN_START or start_guess > MAX_START:
        raise ValueError(f"start_guess must be between {MIN_START} and {MAX_START}")

def _frange(a, b, step):
    x = a
    while x <= b + 1e-9:
        yield x
        x += step

def plan(start_guess:int,
         finals_target:int,
         rounds_desired:int,
         strictness:str='moderate',
         prefer_wc:bool=True,
         allow_wc_down:bool=True,
         allow_start_adjust:bool=False,
         start_adjust_range:int=3,
         r0_delta_pct:float=0.05,
         decay_values:Optional[List[float]]=None,
         wc_extra_try:int=4,
         top_k_per_round:int=DEFAULT_SEQ_TOP_K,
         max_nodes:int=DEFAULT_SEQ_MAX_NODES,
         time_limit:float=DEFAULT_SEQ_TIME_LIMIT,
         tol:int=0) -> Dict[str,Any]:
    """
    Sequential planner (single-process). Keeps core algorithm exactly.
    Returns plan dict with keys: 'rows', 'final_total', '_meta', '_score'.

    Note: For reproducibility pass explicit decay_values, top_k_per_round, max_nodes, time_limit.
    """

    _validate_inputs(start_guess, finals_target, rounds_desired)

    strict_map = {'generous':0.70, 'moderate':0.60, 'stringent':0.50}
    if strictness not in strict_map:
        raise ValueError("strictness must be 'generous','moderate' or 'stringent'")
    r0_base = strict_map[strictness]

    # seeds setup
    deltas = [0.0, -r0_delta_pct, -r0_delta_pct/2.0, r0_delta_pct/2.0, r0_delta_pct]
    if decay_values is None:
        decay_values = [round(x,4) for x in list(_frange(0.60, 0.95, 0.035))]

    starts = [start_guess]
    if allow_start_adjust:
        for s in range(max(finals_target, start_guess - start_adjust_range), start_guess + start_adjust_range + 1):
            if s not in starts:
                starts.append(s)

    combos: List[Tuple[int,float,float]] = []
    for s in starts:
        for delta in deltas:
            r0 = max(0.01, min(0.99, r0_base * (1.0 + delta)))
            for decay in decay_values:
                combos.append((s, r0, decay))

    # run sequentially
    solver = AdaptiveSolverV3(max_nodes=max_nodes)
    solver.time_limit = time_limit

    overall_start = time.time()
    best_plan = None
    best_score = None
    seeds_tried = 0
    for (s, r0, decay) in combos:
        # global cutoff
        if time.time() - overall_start > time_limit:
            break
        plan_dict = solver._search(s, finals_target, rounds_desired, r0, decay, prefer_wc, allow_wc_down, wc_extra_try, top_k_per_round, tol)
        seeds_tried += 1
        if plan_dict is None:
            continue
        final_total = plan_dict['final_total']
        diff = abs(final_total - finals_target)
        wc_excess = sum(max(0, r['wildcards'] - solver._wc_base(r['participants'])) for r in plan_dict['rows'] if r['round'] < rounds_desired)
        packing_waste = sum((r['groups'] * r['group_size'] - r['participants']) for r in plan_dict['rows'] if r['participants'] > 0)
        score = (diff, wc_excess, packing_waste, abs(s - start_guess))
        plan_dict['_score'] = score
        plan_dict['_meta'] = {'mode':'sequential', 'start_used': s, 'r0_used': r0, 'decay_used': decay, 'nodes': solver.nodes_visited, 'time': time.time() - overall_start}
        if best_plan is None or score < best_score:
            best_plan = plan_dict
            best_score = score
        if score[0] == 0 and score[2] == 0 and score[1] == 0:
            break

    if best_plan is None:
        raise RuntimeError("No plan found (sequential)")

    # attach final meta
    best_plan['_meta']['seeds_tried'] = seeds_tried
    best_plan['_meta']['wall_time_total'] = time.time() - overall_start
    best_plan['_meta']['settings_used'] = {'top_k_per_round': top_k_per_round, 'max_nodes': max_nodes, 'time_limit': time_limit}
    return best_plan

def parallel_plan(start_guess:int,
                  finals_target:int,
                  rounds_desired:int,
                  strictness:str='moderate',
                  prefer_wc:bool=True,
                  allow_wc_down:bool=True,
                  allow_start_adjust:bool=False,
                  start_adjust_range:int=3,
                  r0_delta_pct:float=0.05,
                  decay_values:Optional[List[float]]=None,
                  wc_extra_try:int=4,
                  top_k_per_round:Optional[int]=None,
                  max_nodes:Optional[int]=None,
                  time_limit:Optional[float]=None,
                  tol:int=0,
                  max_workers:Optional[int]=None) -> Dict[str,Any]:
    """
    Parallel planner: distributes (start,r0,decay) seeds across worker processes.
    If top_k_per_round, max_nodes or time_limit are None they are auto-tuned (exponential heuristic).
    Returns plan dict with enhanced metadata including total wall time and cores used.
    """

    _validate_inputs(start_guess, finals_target, rounds_desired)

    strict_map = {'generous':0.70, 'moderate':0.60, 'stringent':0.50}
    if strictness not in strict_map:
        raise ValueError("strictness must be 'generous','moderate' or 'stringent'")
    r0_base = strict_map[strictness]

    # auto-tune missing parallel params
    if top_k_per_round is None or max_nodes is None or time_limit is None:
        tune = auto_tune_for_parallel(start_guess, rounds_desired)
        if top_k_per_round is None:
            top_k_per_round = tune['top_k_per_round']
        if max_nodes is None:
            max_nodes = tune['max_nodes']
        if time_limit is None:
            time_limit = tune['time_limit']

    # clamp values
    top_k_per_round = int(max(3, min(60, int(top_k_per_round))))
    max_nodes = int(max(1000, min(10_000_000, int(max_nodes))))
    time_limit = float(max(1.0, min(3600.0, float(time_limit))))

    # seeds
    deltas = [0.0, -r0_delta_pct, -r0_delta_pct/2.0, r0_delta_pct/2.0, r0_delta_pct]
    if decay_values is None:
        decay_values = [round(x,4) for x in list(_frange(0.60, 0.95, 0.035))]

    starts = [start_guess]
    if allow_start_adjust:
        for s in range(max(finals_target, start_guess - start_adjust_range), start_guess + start_adjust_range + 1):
            if s not in starts:
                starts.append(s)

    combos: List[Tuple[int,float,float]] = []
    for s in starts:
        for delta in deltas:
            r0 = max(0.01, min(0.99, r0_base * (1.0 + delta)))
            for decay in decay_values:
                combos.append((s, r0, decay))

    # prepare worker init config
    init_cfg = {
        'wc_pct': 0.10,
        'min_group_size': 12,
        'max_group_size': 20,
        'max_adjust_fraction': 0.05,
        'max_wc_down_abs': 3,
        'max_wc_extra_abs': 6,
        'max_nodes': max_nodes,
        'backtrack_depth': 2
    }

    seeds = []
    for (s, r0, decay) in combos:
        seeds.append({
            'start': s, 'r0': r0, 'decay': decay,
            'finals': finals_target, 'rounds': rounds_desired,
            'prefer_wc': prefer_wc, 'allow_wc_down': allow_wc_down,
            'wc_extra_allow': wc_extra_try, 'top_k': top_k_per_round,
            'tol': tol, 'time_limit': time_limit
        })

    cpu_count = multiprocessing.cpu_count() or 2
    if max_workers is None:
        max_workers = min(cpu_count, len(seeds))
    else:
        max_workers = min(int(max_workers), cpu_count, len(seeds))

    wall_start = time.time()
    best_plan = None
    best_score = None

    # run pool
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker_run_search, init_cfg, seed) for seed in seeds]
        for fut in concurrent.futures.as_completed(futures, timeout=None):
            try:
                res = fut.result()
            except Exception as e:
                # worker crashed unexpectedly -> continue
                # keep robust: print minimal info
                print("[worker crashed]", e)
                continue
            if res is None:
                continue
            if isinstance(res, dict) and res.get('_error'):
                print("[worker error trace]\n", res.get('trace', '<no trace>'))
                continue

            plan = res
            final_total = plan['final_total']
            diff = abs(final_total - finals_target)
            # compute wc_excess using solver wrapper (quick calcs)
            wc_excess = sum(max(0, r['wildcards'] - AdaptiveSolverV3()._wc_base(r['participants'])) for r in plan['rows'] if r['round'] < rounds_desired)
            packing_waste = sum((r['groups'] * r['group_size'] - r['participants']) for r in plan['rows'] if r['participants'] > 0)
            score = (diff, wc_excess, packing_waste, abs(plan.get('_worker_meta',{}).get('start', start_guess) - start_guess))
            plan['_score'] = score
            plan['_meta'] = plan.get('_meta', {})
            plan['_meta']['worker_meta'] = plan.get('_worker_meta', {})
            plan['_meta']['collected_at_since_wall_start'] = time.time() - wall_start

            if best_plan is None or score < best_score:
                best_plan = plan
                best_score = score
            if score[0] == 0 and score[1] == 0 and score[2] == 0:
                break

    if best_plan is None:
        raise RuntimeError("No plan found (parallel)")

    # enhanced metadata
    total_wall_time = time.time() - wall_start
    best_plan['_meta']['mode'] = 'parallel'
    best_plan['_meta']['wall_time_total'] = total_wall_time
    best_plan['_meta']['seeds_tried'] = len(seeds)
    best_plan['_meta']['cores_used'] = max_workers
    best_plan['_meta']['settings_used'] = {'top_k_per_round': top_k_per_round, 'max_nodes': max_nodes, 'time_limit': time_limit}
    return best_plan

# ---------------------------
# if run as script - quick smoke test
# ---------------------------
if __name__ == "__main__":
    # small sequential sanity test - should be quick
    print("Running small sequential test (start=100, finals=12, rounds=5)...")
    p = plan(start_guess=100, finals_target=12, rounds_desired=5, strictness='generous',
             prefer_wc=True, allow_wc_down=True, allow_start_adjust=False,
             r0_delta_pct=0.05, decay_values=None, wc_extra_try=4,
             top_k_per_round=12, max_nodes=300000, time_limit=12.0, tol=0)
    print("Meta:", p.get('_meta'), "score:", p.get('_score'))
    for r in p['rows']:
        print(r)
    print("Final total:", p['final_total'])

    # small parallel example (may take a few seconds)
    print("\nRunning small parallel test (start=100, finals=12, rounds=5) with auto-tune...")
    pp = parallel_plan(start_guess=100, finals_target=12, rounds_desired=5, strictness='generous',
                       prefer_wc=True, allow_wc_down=True, allow_start_adjust=False,
                       r0_delta_pct=0.05, decay_values=None, wc_extra_try=4,
                       top_k_per_round=None, max_nodes=None, time_limit=None, tol=0, max_workers=2)
    print("Parallel meta:", pp.get('_meta'), "score:", pp.get('_score'))
    for r in pp['rows']:
        print(r)
    print("Final total:", pp['final_total'])
