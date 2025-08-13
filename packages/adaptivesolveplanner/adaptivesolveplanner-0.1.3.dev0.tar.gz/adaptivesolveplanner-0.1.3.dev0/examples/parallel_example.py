#!/usr/bin/env python3
"""
Parallel example (uses ProcessPoolExecutor). Keep max_workers small on low-RAM machines.
"""
from adaptive_solve_planner import parallel_plan

def main():
    p = parallel_plan(start_guess=100, finals_target=12, rounds_desired=5, strictness="generous",
                      prefer_wc=True, allow_wc_down=True, top_k_per_round=None, max_nodes=None, time_limit=None, max_workers=2)
    print("Parallel plan meta:", p["_meta"])
    for r in p["rows"]:
        print(r)

if __name__ == "__main__":
    main()
