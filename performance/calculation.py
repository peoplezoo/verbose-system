"""Deterministic calculation engine for performance-engineering simulations."""

from __future__ import annotations

from dataclasses import dataclass

from performance.digital_twin import VehicleDigitalTwin

AIR_DENSITY_KG_M3 = 1.225
GRAVITY_M_S2 = 9.80665
NM_RPM_TO_HP = 7127.0


@dataclass(frozen=True)
class EngineModel:
    """Calculated engine operating estimates."""

    torque_nm: float
    power_hp: float
    bmep_bar: float
    air_mass_g_s: float
    fuel_mass_g_s: float
    lambda_value: float
    injector_duty_cycle: float
    boost_pressure_psi: float
    turbo_efficiency: float
    exhaust_temp_c: float


@dataclass(frozen=True)
class VehicleModel:
    """Calculated vehicle performance estimates."""

    wheel_torque_nm_by_gear: tuple[float, ...]
    wheel_power_hp: float
    zero_to_sixty_s: float
    sixty_to_hundred_s: float
    quarter_mile_s: float
    tractive_force_n_first_gear: float
    traction_limit_n: float
    drivetrain_loss_hp: float


@dataclass(frozen=True)
class ThermalModel:
    """Calculated thermal-load estimates."""

    coolant_load_kw: float
    oil_temperature_tendency_c: float
    intake_air_temperature_c: float
    charge_air_temperature_c: float
    turbo_thermal_load_kw: float
    heat_rejection_kw: float


@dataclass(frozen=True)
class PerformanceResult:
    """Combined calculation output for comparison and optimization."""

    engine: EngineModel
    vehicle: VehicleModel
    thermal: ThermalModel


class CalculationEngine:
    """Pure calculation service; it never writes to an ECU."""

    def calculate(self, twin: VehicleDigitalTwin, rpm: int = 5500, target_lambda: float = 0.82) -> PerformanceResult:
        """Calculate engine, vehicle, and thermal models for a digital twin."""

        engine = self.calculate_engine(twin, rpm=rpm, target_lambda=target_lambda)
        vehicle = self.calculate_vehicle(twin, engine)
        thermal = self.calculate_thermal(twin, engine)
        return PerformanceResult(engine=engine, vehicle=vehicle, thermal=thermal)

    def calculate_engine(self, twin: VehicleDigitalTwin, rpm: int, target_lambda: float) -> EngineModel:
        engine = twin.engine
        boost_ratio = (14.7 + engine.baseline_boost_psi) / 14.7
        torque_nm = engine.baseline_torque_nm
        power_hp = torque_nm * rpm / NM_RPM_TO_HP
        bmep_bar = (torque_nm * 4 * 3.14159) / (engine.displacement_l / 1000) / 100000
        air_mass_g_s = engine.displacement_l * rpm / 120 * boost_ratio * engine.volumetric_efficiency * 1.18
        afr = twin.fuel_system.stoich_afr * target_lambda
        fuel_mass_g_s = air_mass_g_s / afr
        injector_capacity_g_s = twin.fuel_system.injector_capacity_cc_min * engine.cylinders * 0.745 / 60
        duty_cycle = fuel_mass_g_s / injector_capacity_g_s
        exhaust_temp_c = 780 + max(engine.baseline_boost_psi - 8, 0) * 9 + (1 - target_lambda) * 120
        return EngineModel(
            torque_nm=torque_nm,
            power_hp=power_hp,
            bmep_bar=bmep_bar,
            air_mass_g_s=air_mass_g_s,
            fuel_mass_g_s=fuel_mass_g_s,
            lambda_value=target_lambda,
            injector_duty_cycle=duty_cycle,
            boost_pressure_psi=engine.baseline_boost_psi,
            turbo_efficiency=engine.turbocharger.compressor_efficiency,
            exhaust_temp_c=exhaust_temp_c,
        )

    def calculate_vehicle(self, twin: VehicleDigitalTwin, engine: EngineModel) -> VehicleModel:
        drivetrain = twin.drivetrain
        tire_radius = twin.chassis.tire.radius_m
        wheel_torque = tuple(
            engine.torque_nm * ratio * drivetrain.final_drive * drivetrain.drivetrain_efficiency
            for ratio in drivetrain.gear_ratios
        )
        wheel_power_hp = engine.power_hp * drivetrain.drivetrain_efficiency
        tractive_force = wheel_torque[0] / tire_radius
        traction_limit = twin.chassis.mass_kg * GRAVITY_M_S2 * twin.chassis.tire.friction_coefficient
        effective_force = min(tractive_force, traction_limit)
        acceleration = effective_force / twin.chassis.mass_kg
        zero_to_sixty = 26.8224 / max(acceleration * 0.72, 0.1)
        sixty_to_hundred = 17.8816 / max(acceleration * 0.42, 0.1)
        quarter_mile = 6.29 * (twin.chassis.mass_kg * 2.20462 / max(engine.power_hp, 1)) ** (1 / 3)
        drivetrain_loss_hp = engine.power_hp - wheel_power_hp
        return VehicleModel(
            wheel_torque_nm_by_gear=wheel_torque,
            wheel_power_hp=wheel_power_hp,
            zero_to_sixty_s=zero_to_sixty,
            sixty_to_hundred_s=sixty_to_hundred,
            quarter_mile_s=quarter_mile,
            tractive_force_n_first_gear=tractive_force,
            traction_limit_n=traction_limit,
            drivetrain_loss_hp=drivetrain_loss_hp,
        )

    def calculate_thermal(self, twin: VehicleDigitalTwin, engine: EngineModel) -> ThermalModel:
        boost_delta = max(engine.boost_pressure_psi - 8, 0)
        coolant_load_kw = engine.power_hp * 0.7457 * 0.34
        oil_temperature_tendency_c = 100 + boost_delta * 1.8
        intake_air_temperature_c = 25 + boost_delta * 1.2
        charge_air_temperature_c = intake_air_temperature_c + boost_delta * (1 - twin.engine.turbocharger.compressor_efficiency) * 4
        turbo_thermal_load_kw = engine.power_hp * 0.7457 * 0.18
        heat_rejection_kw = coolant_load_kw + turbo_thermal_load_kw
        return ThermalModel(
            coolant_load_kw=coolant_load_kw,
            oil_temperature_tendency_c=oil_temperature_tendency_c,
            intake_air_temperature_c=intake_air_temperature_c,
            charge_air_temperature_c=charge_air_temperature_c,
            turbo_thermal_load_kw=turbo_thermal_load_kw,
            heat_rejection_kw=heat_rejection_kw,
        )
