"""Vehicle state vector for continuously updated diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping


@dataclass(frozen=True)
class VehicleState:
    engine_state: Mapping[str, float] = field(default_factory=dict)
    fuel_state: Mapping[str, float] = field(default_factory=dict)
    air_state: Mapping[str, float] = field(default_factory=dict)
    thermal_state: Mapping[str, float] = field(default_factory=dict)
    electrical_state: Mapping[str, float] = field(default_factory=dict)
    transmission_state: Mapping[str, float] = field(default_factory=dict)
    chassis_state: Mapping[str, float] = field(default_factory=dict)
    network_state: Mapping[str, float] = field(default_factory=dict)
    ecu_state: Mapping[str, str] = field(default_factory=dict)
    fault_state: Mapping[str, str] = field(default_factory=dict)
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
