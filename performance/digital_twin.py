"""Parameterized vehicle digital twin used before any ECU write is considered."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Turbocharger:
    """Turbocharger operating envelope."""

    max_boost_psi: float
    compressor_efficiency: float
    max_shaft_speed_rpm: int | None = None


@dataclass(frozen=True)
class Engine:
    """Engine parameters required for performance calculations."""

    displacement_l: float
    compression_ratio: float
    cylinders: int
    redline_rpm: int
    volumetric_efficiency: float
    baseline_boost_psi: float
    baseline_torque_nm: float
    baseline_power_hp: float
    turbocharger: Turbocharger


@dataclass(frozen=True)
class FuelSystem:
    """Fuel-system limits used by the simulator and constraints."""

    injector_capacity_cc_min: float
    fuel_pressure_bar: float
    fuel_type: str
    stoich_afr: float
    max_injector_duty_cycle: float


@dataclass(frozen=True)
class Drivetrain:
    """Gear and torque-transfer parameters."""

    transmission: str
    gear_ratios: tuple[float, ...]
    final_drive: float
    drivetrain_efficiency: float
    torque_limit_nm: float


@dataclass(frozen=True)
class Tire:
    """Driven tire dimensions and grip estimate."""

    width_mm: int
    aspect_ratio: int
    wheel_diameter_in: int
    friction_coefficient: float

    @property
    def radius_m(self) -> float:
        sidewall_mm = self.width_mm * self.aspect_ratio / 100
        wheel_radius_mm = self.wheel_diameter_in * 25.4 / 2
        return (sidewall_mm + wheel_radius_mm) / 1000


@dataclass(frozen=True)
class Chassis:
    """Vehicle mass and aerodynamic parameters."""

    mass_kg: float
    drag_coefficient: float
    frontal_area_m2: float
    tire: Tire


@dataclass(frozen=True)
class VehicleDigitalTwin:
    """Complete pre-flash model of a vehicle configuration."""

    name: str
    engine: Engine
    fuel_system: FuelSystem
    drivetrain: Drivetrain
    chassis: Chassis

    def with_engine_delta(self, boost_delta_psi: float = 0, torque_delta_nm: float = 0) -> "VehicleDigitalTwin":
        """Return a modified twin without mutating the baseline."""

        return replace(
            self,
            engine=replace(
                self.engine,
                baseline_boost_psi=self.engine.baseline_boost_psi + boost_delta_psi,
                baseline_torque_nm=self.engine.baseline_torque_nm + torque_delta_nm,
            ),
        )
