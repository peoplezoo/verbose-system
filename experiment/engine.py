"""Controlled diagnostic experiment and falsification primitives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExperimentOutcome(StrEnum):
    SUPPORTS = "supports"
    FALSIFIES = "falsifies"
    INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class DiagnosticExperiment:
    hypothesis: str
    prediction: str
    test: str
    risk: float
    cost: float
    information_gain: float

    @property
    def utility(self) -> float:
        return self.information_gain / max(self.cost, 0.001)


@dataclass(frozen=True)
class ExperimentResult:
    experiment: DiagnosticExperiment
    observation: str
    outcome: ExperimentOutcome
