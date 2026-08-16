"""Adaptive calibration helpers for updating the digital twin from measurements."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionError:
    """Difference between predicted and measured vehicle behavior."""

    signal: str
    predicted: float
    measured: float
    units: str

    @property
    def error(self) -> float:
        return self.measured - self.predicted
