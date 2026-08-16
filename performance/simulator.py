"""Tuning simulator for baseline-vs-candidate comparison."""

from __future__ import annotations

from dataclasses import dataclass

from performance.calculation import CalculationEngine, PerformanceResult
from performance.constraints import ConstraintViolation, SafetyConstraints
from performance.digital_twin import VehicleDigitalTwin


@dataclass(frozen=True)
class TuningDelta:
    """Proposed parameter changes to simulate, not flash."""

    boost_delta_psi: float = 0
    torque_delta_nm: float = 0


@dataclass(frozen=True)
class TuningComparison:
    """Baseline/tuned outputs plus safety evaluation."""

    baseline: PerformanceResult
    tuned: PerformanceResult
    violations: tuple[ConstraintViolation, ...]

    @property
    def is_recommendable(self) -> bool:
        return not self.violations

    @property
    def power_delta_hp(self) -> float:
        return self.tuned.engine.power_hp - self.baseline.engine.power_hp

    @property
    def torque_delta_nm(self) -> float:
        return self.tuned.engine.torque_nm - self.baseline.engine.torque_nm


class TuningSimulator:
    """Simulate and validate a candidate calibration without ECU writes."""

    def __init__(
        self,
        calculation_engine: CalculationEngine | None = None,
        constraints: SafetyConstraints | None = None,
    ) -> None:
        self.calculation_engine = calculation_engine or CalculationEngine()
        self.constraints = constraints or SafetyConstraints()

    def simulate(self, twin: VehicleDigitalTwin, delta: TuningDelta, rpm: int = 5500) -> TuningComparison:
        """Compare a baseline twin with a modified candidate model."""

        baseline = self.calculation_engine.calculate(twin, rpm=rpm)
        candidate = twin.with_engine_delta(
            boost_delta_psi=delta.boost_delta_psi,
            torque_delta_nm=delta.torque_delta_nm,
        )
        tuned = self.calculation_engine.calculate(candidate, rpm=rpm)
        violations = self.constraints.evaluate(candidate, tuned)
        return TuningComparison(baseline=baseline, tuned=tuned, violations=violations)
