# AdaptiveSolvePlanner

AdaptiveSolvePlanner is a production-oriented adaptive tournament planner and solver. It supports sequential and process-parallel search over retention/decay parameters to produce "nice" tournament round plans (groups, qualifiers, wildcards) while honoring configurable limits.

[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://www.python.org/)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

## Quickstart

To install from PyPI:

```bash
python -m pip install adaptivesolveplanner
```

To install latest from GitHub:

```bash
pip install git+https://github.com/Smoki-Cool/adaptivesolveplanner.git
```

## Example:

```python
from adaptive_solve_planner import plan

p = plan(start_guess=100, finals_target=12, rounds_desired=5, strictness="generous",
         prefer_wc=True, allow_wc_down=True, top_k_per_round=12, max_nodes=300000, time_limit=12.0)
print(p["_meta"])
for r in p["rows"]:
    print(r)
```

## API

Two primary entry points:
* `plan(...)` — sequential single-process planner
* `parallel_plan(...)` — process-parallel planner with auto-tuning

Both return a dict with:
* `rows` — per-round dicts
* `final_total` — final number of players
* `_meta` — diagnostic metadata
* `_score` — score used for selecting best plan

See `examples/` for runnable samples.

## Configuration

`PlannerConfig` centralizes defaults and can be overridden from environment variables using the `ASP_` prefix (e.g. `ASP_WC_PCT=0.12`). See `adaptive_solve_planner/config.py`.

## CLI

If you installed the package with the console script, run:

```bash
adaptivesolveplanner --help
```

## Development

Create a virtualenv, install dev requirements, run tests:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install build twine pytest
python -m pytest
```

## Contributing

See `CONTRIBUTING.md`.

## License

This project is licensed under the GNU General Public License v3.0 — see the `LICENSE` file.