# python adaptive_solve_planner/__init__.py
"""
AdaptiveSolvePlanner public package API.

Expose `plan` and `parallel_plan` as stable entry points and the core solver class
for advanced users who want to instantiate and tune manually.
"""

from importlib.metadata import version, PackageNotFoundError

from .api import plan, parallel_plan
from .core import AdaptiveSolverV3
from .config import PlannerConfig

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "0.1.0"  # fallback for dev environment

__all__ = [
    "__version__",
    "plan", 
    "parallel_plan", 
    "AdaptiveSolverV3", 
    "PlannerConfig"
]
