# python adaptive_solve_planner/config.py
"""
Planner configuration using pydantic v2 + pydantic-settings.

This settings class centralizes all tunable defaults and can be overridden
via environment variables prefixed with `ASP_` (e.g. `ASP_WC_PCT=0.12`).

Requires:
    pip install pydantic pydantic-settings

See README or docs for full environment variable mapping.
"""
from __future__ import annotations
from typing import Dict, Any, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PlannerConfig(BaseSettings):
    """Global configuration for AdaptiveSolvePlanner.

    Values can be overridden with environment variables using the `ASP_` prefix.
    Example: `ASP_WC_PCT=0.12` to override `wc_pct`.
    """

    # Core solver tunables
    wc_pct: float = Field(0.10, description="Base wildcard percentage")
    min_group_size: int = Field(12, description="Minimum allowed group size")
    max_group_size: int = Field(20, description="Maximum allowed group size")
    max_adjust_fraction: float = Field(0.05, description="Max per-round small adjustment fraction")
    max_wc_down_abs: int = Field(3, description="Max wildcard downward adjustment (absolute)")
    max_wc_extra_abs: int = Field(6, description="Max wildcard upward adjustment (absolute)")
    backtrack_depth: int = Field(2, description="Backtracking depth for DFS (not heavily used)")

    # Defaults for API auto-tuning / sequential mode
    default_max_nodes: int = Field(300000, description="Default maximum node visits for searches")
    default_top_k: int = Field(12, description="Default top_k_per_round")
    default_time_limit: float = Field(12.0, description="Default time limit (seconds) for searches")

    # Safety limits
    min_start: int = Field(2, description="Minimum allowed start participants")
    max_start: int = Field(10000, description="Maximum allowed start participants")
    min_rounds: int = Field(2, description="Minimum allowed rounds")
    max_rounds: int = Field(16, description="Maximum allowed rounds")

    # pydantic-settings config: environment variable prefix and immutability
    model_config = SettingsConfigDict(env_prefix="ASP_", frozen=True)

    def to_worker_init_cfg(self, max_nodes_override: Optional[int] = None) -> Dict[str, Any]:
        """
        Convert the PlannerConfig into the serializable init_cfg expected by workers.

        If max_nodes_override is provided, it will be used as the worker's max_nodes;
        otherwise use the config's default_max_nodes.
        """
        return {
            "wc_pct": float(self.wc_pct),
            "min_group_size": int(self.min_group_size),
            "max_group_size": int(self.max_group_size),
            "max_adjust_fraction": float(self.max_adjust_fraction),
            "max_wc_down_abs": int(self.max_wc_down_abs),
            "max_wc_extra_abs": int(self.max_wc_extra_abs),
            "max_nodes": int(max_nodes_override or self.default_max_nodes),
            "backtrack_depth": int(self.backtrack_depth),
        }
