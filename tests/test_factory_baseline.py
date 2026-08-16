from dataclasses import replace

from baseline.models import CalibrationDataReference, CodingConfiguration, EcuBaselineData, RestoreLevel
from baseline.service import FactoryBaselineService
from baseline.vault import InMemoryBaselineVault
from safety.gate import SafetyCheck, SafetyGate, SafetyGateRequest
from vehicle.interface import SimulatedBmwInterface


def build_baseline():
    snapshot = SimulatedBmwInterface().collect_snapshot()
    vault = InMemoryBaselineVault()
    service = FactoryBaselineService(vault)
    baseline = service.create_factory_baseline(
        snapshot,
        mileage_km=42_000,
        ecu_data=(EcuBaselineData(address="0x12", name="DME", hardware_number="HW-1", software_version="SW-1"),),
        calibration_references=(
            CalibrationDataReference(
                ecu_address="0x12",
                calibration_id="CAL-1",
                checksum="abc123",
                backup_available=True,
                recovery_image_uri="vault://factory/dme",
            ),
        ),
        coding_configuration=(CodingConfiguration(ecu_address="0x40", options={"market": "US"}),),
        diagnostic_configuration={"tool": "simulated"},
    )
    return snapshot, vault, service, baseline


def test_factory_baseline_is_created_before_tuning_version():
    _snapshot, _vault, service, baseline = build_baseline()

    version = service.create_tuning_version(
        baseline.baseline_id,
        version_number=2,
        description="Validated torque increase simulation",
        proposed_by="llm",
    )

    assert baseline.baseline_id.value == "FACTORY-0001"
    assert len(baseline.baseline_hash) == 64
    assert version.version_id == "TUNE-0002"
    assert version.parent_version_id == "FACTORY-0001"


def test_factory_baseline_is_immutable_and_hash_verified():
    _snapshot, vault, _service, baseline = build_baseline()

    try:
        vault.store_factory_baseline(baseline)
    except PermissionError as exc:
        assert "immutable" in str(exc)
    else:
        raise AssertionError("factory baseline must not be overwritten")

    tampered = replace(baseline, vin="WBA-TAMPERED")
    vault.tamper_for_test(baseline.baseline_id, tampered)

    try:
        vault.get_factory_baseline(baseline.baseline_id)
    except Exception as exc:
        assert "integrity" in str(exc).lower()
    else:
        raise AssertionError("tampered baseline must fail integrity verification")


def test_restore_level_does_not_fabricate_missing_calibration_data():
    snapshot = SimulatedBmwInterface().collect_snapshot()
    vault = InMemoryBaselineVault()
    service = FactoryBaselineService(vault)
    baseline = service.create_factory_baseline(
        snapshot,
        coding_configuration=(CodingConfiguration(ecu_address="0x40", options={"market": "US"}),),
        calibration_references=(CalibrationDataReference(ecu_address="0x12", calibration_id="CAL-1"),),
    )

    assert service.restore_level_for(baseline) == RestoreLevel.CONFIGURATION


def test_safety_gate_requires_every_pre_write_check():
    snapshot, vault, service, baseline = build_baseline()
    gate = SafetyGate(vault)

    result = gate.evaluate(
        SafetyGateRequest(
            vin=snapshot.vehicle.vin,
            target_ecu=snapshot.ecus[0],
            baseline=baseline,
            current_ecu_state_captured=True,
            proposed_change_validated=True,
            power_communication_valid=True,
            restore_level=service.restore_level_for(baseline),
            user_authorized=False,
        )
    )

    assert not result.passed
    assert result.missing_checks == (SafetyCheck.USER_AUTHORIZATION,)
