"""Computer-vision observation models for screens, diagrams, and physical inspection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionObservation:
    source: str
    observation_type: str
    structured_observation: str
    diagnostic_graph_ref: str | None = None
