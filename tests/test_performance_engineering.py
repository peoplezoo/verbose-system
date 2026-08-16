from performance.constraints import SafetyConstraints
from performance.digital_twin import (
    Chassis,
    Drivetrain,
    Engine,
    FuelSystem,
    Tire,
    Turbocharger,
    VehicleDigitalTwin,
)
from performance.simulator import TuningDelta, TuningSimulator
from safety.permissions import require_no_ecu_write


def build_twin() -> VehicleDigitalTwin:
    return VehicleDigitalTwin(
        name="Example BMW B58",
        engine=Engine(
            displacement_l=3.0,
            compression_ratio=11.0,
            cylinders=6,
            redline_rpm=7000,
            volumetric_efficiency=0.95,
            baseline_boost_psi=12.0,
            baseline_torque_nm=400.0,
            baseline_power_hp=335.0,
            turbocharger=Turbocharger(max_boost_psi=18.0, compressor_efficiency=0.72),
        ),
        fuel_system=FuelSystem(
            injector_capacity_cc_min=1_200,
            fuel_pressure_bar=200.0,
            fuel_type="gasoline",
            stoich_afr=14.7,
            max_injector_duty_cycle=0.90,
        ),
        drivetrain=Drivetrain(
            transmission="8HP",
            gear_ratios=(5.0, 3.2, 2.14, 1.72, 1.31, 1.0, 0.82, 0.64),
            final_drive=3.15,
            drivetrain_efficiency=0.86,
            torque_limit_nm=550.0,
        ),
        chassis=Chassis(
            mass_kg=1_700,
            drag_coefficient=0.29,
            frontal_area_m2=2.2,
            tire=Tire(width_mm=255, aspect_ratio=35, wheel_diameter_in=19, friction_coefficient=1.0),
        ),
    )


def test_tuning_simulator_compares_baseline_and_candidate_without_writes():
    twin = build_twin()
    comparison = TuningSimulator().simulate(twin, TuningDelta(boost_delta_psi=3.0, torque_delta_nm=50.0))

    assert comparison.torque_delta_nm == 50.0
    assert comparison.power_delta_hp > 35.0
    assert comparison.tuned.engine.boost_pressure_psi == 15.0
    assert comparison.tuned.vehicle.zero_to_sixty_s < comparison.baseline.vehicle.zero_to_sixty_s
    assert comparison.is_recommendable


def test_constraints_reject_unsafe_candidate():
    twin = build_twin()
    simulator = TuningSimulator(constraints=SafetyConstraints(max_boost_psi=13.0, max_transmission_torque_nm=425.0))
    comparison = simulator.simulate(twin, TuningDelta(boost_delta_psi=4.0, torque_delta_nm=80.0))

    assert not comparison.is_recommendable
    assert {violation.name for violation in comparison.violations} >= {"boost_pressure", "transmission_torque"}


def test_ecu_write_operations_are_isolated_from_simulation():
    try:
        require_no_ecu_write("write_calibration")
    except PermissionError as exc:
        assert "isolated from simulation" in str(exc)
    else:
        raise AssertionError("simulation layer must not allow ECU writes")
