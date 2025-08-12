# python adaptive_solve_planner/core.py
"""
Core solver logic (AdaptiveSolverV3).

This module contains the DFS/backtracking solver that generates candidate
group/qualifier/wildcard plans for each round and searches for an overall
multi-round plan that matches the user's targets.
"""

from __future__ import annotations
import math
import time
from typing import List, Dict, Any, Optional, Tuple

from .utils import ceil_div  # local helper


class AdaptiveSolverV3:
    """Core solver implementing DFS/backtracking tournament planner."""

    PREFERRED_QPG = [16, 15, 14, 12, 10, 8, 6, 5, 4, 3]
    PREFERRED_GROUP_SIZES = [20, 16, 18, 12]

    def __init__(
        self,
        wc_pct: float = 0.10,
        min_group_size: int = 12,
        max_group_size: int = 20,
        max_adjust_fraction: float = 0.05,
        max_wc_down_abs: int = 3,
        max_wc_extra_abs: int = 6,
        max_nodes: int = 300000,
        backtrack_depth: int = 2,
    ) -> None:
        # Basic configuration
        self.wc_pct = float(wc_pct)
        self.min_g = int(min_group_size)
        self.max_g = int(max_group_size)
        self.max_adjust_fraction = float(max_adjust_fraction)
        self.max_wc_down_abs = int(max_wc_down_abs)
        self.max_wc_extra_abs = int(max_wc_extra_abs)
        self.max_nodes = int(max_nodes)
        self.backtrack_depth = int(backtrack_depth)

        # runtime state
        self.nodes_visited: int = 0
        self.start_time: float = 0.0
        self.time_limit: float = 12.0

    def _ceil_div(self, a: int, b: int) -> int:
        """Ceiling division helper (delegates to utils.ceil_div)."""
        return ceil_div(a, b)

    def _wc_base(self, participants: int) -> int:
        """Base wildcard rounding logic."""
        if participants <= 1:
            return 0
        return max(1, int(round(participants * self.wc_pct)))

    def _wc_limits(self, participants: int, allow_extra: int, allow_down: bool) -> Tuple[int, int]:
        """Compute allowed wildcard range for given participants."""
        base = self._wc_base(participants)
        extra = min(self.max_wc_extra_abs, allow_extra)
        down = min(self.max_wc_down_abs if allow_down else 0, int(math.floor(participants * 0.05)))
        wc_min = max(0, base - down)
        wc_max = min(participants - 1, base + extra)
        return wc_min, wc_max

    def _is_preferred_multiple(self, val: int) -> bool:
        """Check if val is divisible by one of preferred group sizes."""
        for s in self.PREFERRED_GROUP_SIZES:
            if s > 0 and val % s == 0:
                return True
        return False

    def _group_candidates(self, participants: int) -> List[int]:
        """Generate possible group counts from 1..max_groups."""
        max_groups = max(1, self._ceil_div(participants, self.min_g))
        return list(range(1, max_groups + 1))

    def _try_round_candidates(
        self,
        participants: int,
        desired_qual: int,
        prev_qpg: Optional[int],
        wc_min: int,
        wc_max: int,
        prefer_wc: bool,
        top_k: int = 8,
    ) -> List[Dict[str, Any]]:
        """Generate and score candidate plans for a single round."""
        allowed_adj = min(5, max(1, int(self.max_adjust_fraction * participants)))
        candidates: List[Dict[str, Any]] = []
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
                    candidates.append(
                        {
                            "groups": groups,
                            "group_size": actual_group_size,
                            "qpg": qpg,
                            "qualifiers_total": qualifiers_total,
                            "wildcards": wc,
                            "next_total": next_total,
                            "score": score,
                        }
                    )

        candidates.sort(key=lambda c: c["score"])
        return candidates[:top_k]

    def _search(
        self,
        start: int,
        finals: int,
        rounds: int,
        r0: float,
        decay: float,
        prefer_wc: bool,
        allow_wc_down: bool,
        wc_extra_allow: int,
        top_k: int,
        tol: int,
    ) -> Optional[Dict[str, Any]]:
        """DFS/backtracking search that returns the best plan for given seed params."""
        self.nodes_visited = 0
        self.start_time = time.time()
        best_plan: Optional[Dict[str, Any]] = None
        best_score: Optional[Tuple[int, int, int]] = None

        def dfs(round_idx: int, participants: int, prev_qpg: Optional[int], rows: List[Dict[str, Any]]) -> None:
            nonlocal best_plan, best_score
            if time.time() - self.start_time > self.time_limit or self.nodes_visited > self.max_nodes:
                return
            self.nodes_visited += 1

            if round_idx == rounds:
                final_total = participants
                diff = abs(final_total - finals)
                wc_excess = sum(max(0, r["wildcards"] - self._wc_base(r["participants"])) for r in rows if r["round"] < rounds)
                packing_waste = sum((r["groups"] * r["group_size"] - r["participants"]) for r in rows if r["participants"] > 0)
                score = (diff, wc_excess, packing_waste)
                if best_plan is None or score < best_score:
                    plan = {"rows": [dict(r) for r in rows], "final_total": final_total, "score": score}
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
                if cand["next_total"] >= participants:
                    continue
                row = {
                    "round": round_idx,
                    "participants": participants,
                    "groups": cand["groups"],
                    "group_size": cand["group_size"],
                    "qualifiers_per_group": cand["qpg"],
                    "qualifiers_total": cand["qualifiers_total"],
                    "wildcards": cand["wildcards"],
                    "next_total": cand["next_total"],
                    "retention": round(r, 6),
                }
                rows.append(row)
                dfs(round_idx + 1, cand["next_total"], cand["qpg"], rows)
                rows.pop()
                if time.time() - self.start_time > self.time_limit or self.nodes_visited > self.max_nodes:
                    return

        dfs(1, start, None, [])
        return best_plan
