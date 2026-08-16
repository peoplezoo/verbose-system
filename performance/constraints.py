"""Safety constraints for proposed tuning simulations."""

from __future__ import annotations

from dataclasses import dataclass

from performance.calculation import PerformanceResult
from performance.digital_twin import VehicleDigitalTwin


@dataclass(frozen=True)
class ConstraintViolation:
    """A violated pre-flash tuning constraint."""

    name: str
    actual: float
    limit: float
    units: str


@dataclass(frozen=True)
class SafetyConstraints:
    """Limits that candidate tunes must satisfy before recommendation."""

    max_injector_duty_cycle: float = 0.90
    max_boost_psi: float | None = None
    max_transmission_torque_nm: float | None = None
    max_charge_air_temperature_c: float = 65
    max_oil_temperature_tendency_c: float = 125

    def evaluate(self, twin: VehicleDigitalTwin, result: PerformanceResult) -> tuple[ConstraintViolation, ...]:
        """Return all violated limits for a simulated setup."""

        boost_limit = self.max_boost_psi or twin.engine.turbocharger.max_boost_psi
        torque_limit = self.max_transmission_torque_nm or twin.drivetrain.torque_limit_nm
        checks = [
            ("injector_duty_cycle", result.engine.injector_duty_cycle, self.max_injector_duty_cycle, "ratio"),
            ("boost_pressure", result.engine.boost_pressure_psi, boost_limit, "psi"),
            ("transmission_torque", result.engine.torque_nm, torque_limit, "Nm"),
            ("charge_air_temperature", result.thermal.charge_air_temperature_c, self.max_charge_air_temperature_c, "degC"),
            ("oil_temperature_tendency", result.thermal.oil_temperature_tendency_c, self.max_oil_temperature_tendency_c, "degC"),
        ]
        return tuple(
            ConstraintViolation(name=name, actual=actual, limit=limit, units=units)
            for name, actual, limit, units in checks
            if actual > limit
        )
