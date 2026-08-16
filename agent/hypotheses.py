"""Causal hypotheses with evidence-tied uncertainty."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceStatus(StrEnum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    ASSUMED = "assumed"
    UNKNOWN = "unknown"
    CONTRADICTED = "contradicted"


@dataclass(frozen=True)
class Evidence:
    description: str
    status: EvidenceStatus
    weight: float
    provenance_ref: str | None = None


@dataclass(frozen=True)
class CausalHypothesis:
    cause: str
    mechanism: str
    observations: tuple[Evidence, ...]
    proposed_tests: tuple[str, ...]
    confidence: float

    def normalized_confidence(self) -> float:
        return min(max(self.confidence, 0.0), 1.0)
