"""Knowledge graph primitives for DTC, wiring, parts, and procedures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProvenanceKind(StrEnum):
    BMW_OFFICIAL = "bmw_official_documentation"
    ISTA_RESULT = "ista_result"
    VEHICLE_MEASUREMENT = "vehicle_measurement"
    ENGINEERING_CALCULATION = "engineering_calculation"
    AI_INFERENCE = "ai_inference"
    THIRD_PARTY = "third_party_documentation"
    TECHNICIAN_OBSERVATION = "technician_observation"


@dataclass(frozen=True)
class Provenance:
    kind: ProvenanceKind
    reference: str
    confidence: float = 1.0


@dataclass(frozen=True)
class DtcNode:
    code: str
    ecu: str
    subsystem: str
    symptoms: tuple[str, ...]
    possible_causes: tuple[str, ...]
    measurements: tuple[str, ...]
    test_procedures: tuple[str, ...]
    related_dtcs: tuple[str, ...]
    wiring_refs: tuple[str, ...]
    components: tuple[str, ...]
    repair_procedures: tuple[str, ...]
    provenance: Provenance


@dataclass(frozen=True)
class WiringEdge:
    source_component: str
    source_connector: str
    source_pin: str
    wire_id: str
    junction: str | None
    target_connector: str
    target_pin: str
    target_component: str
    provenance: Provenance


@dataclass(frozen=True)
class PartRecord:
    part_number: str
    supersessions: tuple[str, ...]
    compatibility: tuple[str, ...]
    vehicle_applicability: tuple[str, ...]
    ecu_compatibility: tuple[str, ...]
    component_location: str | None
    installation_procedure: str | None
    torque_specifications: tuple[str, ...]
    provenance: Provenance


@dataclass(frozen=True)
class ServiceProcedure:
    procedure_id: str
    action: str
    required_authorization: str
    steps: tuple[str, ...]
    verification: tuple[str, ...]
    provenance: Provenance
