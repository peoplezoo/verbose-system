"""Temporal measurement sequence primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TemporalMeasurement:
    signal: str
    value: float
    units: str
    observed_at: datetime
