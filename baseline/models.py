"""Immutable baseline and version-history domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from vehicle.ecu import DiagnosticSnapshot, FaultMemoryEntry


class BaselineIntegrityError(RuntimeError):
    """Raised when a baseline cannot be trusted."""


class BaselineKind(StrEnum):
    """Distinguishes readable diagnostics from true calibration/programming backups."""

    DIAGNOSTIC = "diagnostic"
    CALIBRATION_REFERENCE = "calibration_reference"
    CODING_CONFIGURATION = "coding_configuration"


class RestoreLevel(StrEnum):
    """Restore hierarchy for safe recovery planning."""

    CONFIGURATION = "level_1_configuration_restore"
    CALIBRATION = "level_2_calibration_restore"
    FACTORY_SOFTWARE = "level_3_factory_software_recovery"


@dataclass(frozen=True)
class FactoryBaselineId:
    """Stable identifier for the immutable factory baseline."""

    value: str


@dataclass(frozen=True)
class EcuBaselineData:
    """ECU identifiers captured during factory-baseline creation."""

    address: str
    name: str
    hardware_number: str | None = None
    software_version: str | None = None
    part_number: str | None = None
    calibration_id: str | None = None
    coding_index: str | None = None


@dataclass(frozen=True)
class CalibrationDataReference:
    """Reference to original calibration data, not proof of a full recovery image."""

    ecu_address: str
    calibration_id: str
    checksum: str | None = None
    backup_available: bool = False
    recovery_image_uri: str | None = None


@dataclass(frozen=True)
class CodingConfiguration:
    """Captured coding/configuration for a module."""

    ecu_address: str
    options: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", MappingProxyType(dict(self.options)))


@dataclass(frozen=True)
class MeasurementRecord:
    """Baseline live measurement captured before tuning."""

    signal: str
    value: float
    units: str


@dataclass(frozen=True)
class BaselineRecord:
    """Immutable per-vehicle factory baseline record.

    Diagnostic metadata, coding/configuration, and calibration references are kept
    distinct because reading ECU information is not equivalent to owning a
    complete factory recovery image.
    """

    baseline_id: FactoryBaselineId
    vin: str
    created_at: datetime
    mileage_km: int | None
    diagnostic_snapshot: DiagnosticSnapshot
    ecu_data: tuple[EcuBaselineData, ...]
    calibration_references: tuple[CalibrationDataReference, ...]
    coding_configuration: tuple[CodingConfiguration, ...]
    diagnostic_configuration: Mapping[str, Any]
    original_faults: tuple[FaultMemoryEntry, ...]
    original_measurements: tuple[MeasurementRecord, ...]
    baseline_hash: str
    version: int = 1
    kinds: tuple[BaselineKind, ...] = (
        BaselineKind.DIAGNOSTIC,
        BaselineKind.CALIBRATION_REFERENCE,
        BaselineKind.CODING_CONFIGURATION,
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostic_configuration", MappingProxyType(dict(self.diagnostic_configuration)))


@dataclass(frozen=True)
class TuningVersion:
    """Version-controlled tuning change rooted at a factory baseline."""

    version_id: str
    baseline_id: FactoryBaselineId
    parent_version_id: str
    description: str
    proposed_by: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_restore_point: bool = False
