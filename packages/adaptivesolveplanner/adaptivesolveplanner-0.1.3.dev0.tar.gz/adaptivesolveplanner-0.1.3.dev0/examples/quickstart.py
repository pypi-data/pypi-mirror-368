#!/usr/bin/env python3
"""
Quickstart example for AdaptiveSolvePlanner.
"""
from adaptive_solve_planner import plan

def main():
    p = plan(start_guess=100, finals_target=12, rounds_desired=5, strictness="generous",
             prefer_wc=True, allow_wc_down=True, top_k_per_round=12, max_nodes=300000, time_limit=12.0)
    print("Plan meta:", p["_meta"])
    for r in p["rows"]:
        print(r)
    print("Final total:", p["final_total"])

if __name__ == "__main__":
    main()
