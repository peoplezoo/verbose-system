"""Vehicle identity and configuration models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from hardware.topology import BmwBusTopology
from vehicle.ecu import Ecu


@dataclass(frozen=True)
class VehicleIdentity:
    vin: str
    model: str
    model_year: int
    production_date: date | None
    engine: str
    transmission: str
    drivetrain: str
    option_codes: tuple[str, ...]
    vehicle_order: str | None
    ilevel: str | None
    software_levels: tuple[str, ...]
    ecu_hardware: tuple[str, ...]
    ecu_software: tuple[str, ...]
    topology: BmwBusTopology
    market: str
    emissions_configuration: str | None
    ecu_inventory: tuple[Ecu, ...]
