"""Fleet-learning aggregate models using anonymized vehicle observations."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FleetPattern:
    population: str
    symptom: str
    correlated_components: tuple[str, ...]
    hypothesis: str
    sample_size: int
