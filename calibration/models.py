"""Calibration database and change-record models."""

from __future__ import annotations

from dataclasses import dataclass

from knowledge.graph import Provenance


@dataclass(frozen=True)
class CalibrationParameter:
    name: str
    value: float | str
    units: str | None
    lower_limit: float | None = None
    upper_limit: float | None = None


@dataclass(frozen=True)
class CalibrationRecord:
    calibration_id: str
    vehicle_vin: str
    ecu_address: str
    software_version: str
    map_definitions: tuple[str, ...]
    parameters: tuple[CalibrationParameter, ...]
    dependencies: tuple[str, ...]
    checksum: str | None
    version: str
    provenance: Provenance


@dataclass(frozen=True)
class CalibrationChange:
    parameter: str
    before: float | str
    after: float | str
    reason: str
    validation_ref: str | None = None
