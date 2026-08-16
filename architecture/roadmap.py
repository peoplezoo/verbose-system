"""System-domain map and implementation roadmap."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SystemDomain(StrEnum):
    VEHICLE = "vehicle"
    HARDWARE = "hardware"
    PROTOCOLS = "protocols"
    BMW_SOFTWARE = "bmw_software"
    KNOWLEDGE = "knowledge"
    DIAGNOSTICS = "diagnostics"
    CAUSAL_REASONING = "causal_reasoning"
    DIGITAL_TWIN = "digital_twin"
    SIMULATION = "simulation"
    PERFORMANCE = "performance"
    CALIBRATION = "calibration"
    VALIDATION = "validation"
    SAFETY = "safety"
    VERSIONING = "versioning"
    RECOVERY = "recovery"
    AUDIT_SECURITY = "audit_security"
    AI_ORCHESTRATION = "ai_orchestration"


@dataclass(frozen=True)
class RoadmapStage:
    """Ordered implementation stage with write-safety classification."""

    code: str
    name: str
    domains: tuple[SystemDomain, ...]
    read_only: bool
    allows_ecu_writes: bool = False


IMPLEMENTATION_ROADMAP = (
    RoadmapStage("V0", "Hardware + protocol abstraction", (SystemDomain.HARDWARE, SystemDomain.PROTOCOLS), True),
    RoadmapStage("V1", "Vehicle identification + ECU topology", (SystemDomain.VEHICLE,), True),
    RoadmapStage("V2", "Read-only diagnostics", (SystemDomain.DIAGNOSTICS,), True),
    RoadmapStage("V3", "BMW knowledge/wiring/test-plan graph", (SystemDomain.KNOWLEDGE,), True),
    RoadmapStage("V4", "Diagnostic reasoning + falsification engine", (SystemDomain.CAUSAL_REASONING,), True),
    RoadmapStage("V5", "Digital twin + calculations", (SystemDomain.DIGITAL_TWIN, SystemDomain.SIMULATION), True),
    RoadmapStage("V6", "Performance simulation", (SystemDomain.PERFORMANCE,), True),
    RoadmapStage("V7", "Calibration/version-control system", (SystemDomain.CALIBRATION, SystemDomain.VERSIONING), True),
    RoadmapStage("V8", "Factory baseline + recovery", (SystemDomain.RECOVERY, SystemDomain.VERSIONING), True),
    RoadmapStage("V9", "Controlled coding/programming", (SystemDomain.VALIDATION, SystemDomain.SAFETY), False, True),
    RoadmapStage("V10", "Autonomous closed-loop engineering agent", (SystemDomain.AI_ORCHESTRATION,), False, True),
)


def assert_read_only_foundation_before_writes(stages: tuple[RoadmapStage, ...] = IMPLEMENTATION_ROADMAP) -> None:
    """Validate that no ECU-write stage appears before V0-V8 read-only foundations."""

    write_index = next(index for index, stage in enumerate(stages) if stage.allows_ecu_writes)
    earlier = stages[:write_index]
    if not all(stage.read_only and not stage.allows_ecu_writes for stage in earlier):
        raise ValueError("Read-only diagnostic foundation must precede ECU-write capability")
