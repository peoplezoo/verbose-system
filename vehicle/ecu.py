"""ECU domain models for deterministic BMW diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Ecu:
    """A discovered electronic control unit."""

    address: str
    name: str
    variant: str | None = None
    protocol: str = "UDS"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FreezeFrame:
    """Snapshot captured when a diagnostic trouble code was recorded."""

    values: dict[str, Any]


@dataclass(frozen=True)
class FaultMemoryEntry:
    """Structured diagnostic trouble-code entry from an ECU."""

    ecu_address: str
    ecu_name: str
    code: str
    description: str
    status: str
    severity: str = "unknown"
    freeze_frame: FreezeFrame | None = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class VehicleIdentification:
    """Vehicle identity data read from the diagnostic interface."""

    vin: str
    source: str = "diagnostic_interface"


@dataclass(frozen=True)
class DiagnosticSnapshot:
    """V0.1 output: BMW -> interface -> structured diagnostic data."""

    vehicle: VehicleIdentification
    ecus: list[Ecu]
    faults: list[FaultMemoryEntry]
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
