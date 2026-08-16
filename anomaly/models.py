"""Anomaly detection primitives for pre-DTC behavior changes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Anomaly:
    signal: str
    baseline_value: float
    observed_value: float
    deviation: float
    context: str
