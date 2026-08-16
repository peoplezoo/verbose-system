"""Optimization primitives for future Pareto-frontier candidate tunes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OptimizationObjective:
    """Weighted tuning objective; constraints are evaluated separately."""

    power: float = 1.0
    reliability: float = 1.0
    response: float = 1.0
