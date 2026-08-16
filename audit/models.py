"""Audit and reproducibility records for forensic AI decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping


@dataclass(frozen=True)
class ReproducibilityContext:
    model: str
    model_version: str
    system_prompt_version: str
    tool_versions: Mapping[str, str]
    bmw_software_version: str | None
    vehicle_state_hash: str
    calculation_version: str | None
    knowledge_base_version: str | None


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    vehicle_id: str
    vin: str
    ecu: str | None
    operator: str
    ai_model: str | None
    tool: str
    request: str
    result: str
    before_state: str | None
    after_state: str | None
    authorization: str | None
    validation: str | None
    reproducibility: ReproducibilityContext | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
