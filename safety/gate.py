"""Mandatory safety gate for every ECU write attempt."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from baseline.models import BaselineRecord, RestoreLevel
from baseline.vault import BaselineVault
from vehicle.ecu import Ecu


class SafetyCheck(StrEnum):
    CORRECT_VIN = "correct_vin"
    CORRECT_ECU = "correct_ecu"
    FACTORY_BASELINE_EXISTS = "factory_baseline_exists"
    BASELINE_INTEGRITY_VERIFIED = "baseline_integrity_verified"
    CURRENT_ECU_STATE_CAPTURED = "current_ecu_state_captured"
    PROPOSED_CHANGE_VALIDATED = "proposed_change_validated"
    POWER_COMMUNICATION_VALID = "power_communication_conditions_valid"
    RESTORE_PATH_AVAILABLE = "restore_path_available"
    USER_AUTHORIZATION = "user_authorization"


@dataclass(frozen=True)
class SafetyGateRequest:
    """Evidence required before a write-capable ECU action can proceed."""

    vin: str
    target_ecu: Ecu
    baseline: BaselineRecord
    current_ecu_state_captured: bool
    proposed_change_validated: bool
    power_communication_valid: bool
    restore_level: RestoreLevel | None
    user_authorized: bool


@dataclass(frozen=True)
class SafetyGateResult:
    """Pass/fail outcome listing missing write prerequisites."""

    passed: bool
    missing_checks: tuple[SafetyCheck, ...]


class SafetyGate:
    """Verifies every pre-write condition and stops on failure."""

    def __init__(self, vault: BaselineVault) -> None:
        self.vault = vault

    def evaluate(self, request: SafetyGateRequest) -> SafetyGateResult:
        missing: list[SafetyCheck] = []
        if request.vin != request.baseline.vin:
            missing.append(SafetyCheck.CORRECT_VIN)
        if request.target_ecu.address not in {ecu.address for ecu in request.baseline.diagnostic_snapshot.ecus}:
            missing.append(SafetyCheck.CORRECT_ECU)
        try:
            self.vault.get_factory_baseline(request.baseline.baseline_id)
        except (KeyError, PermissionError):
            missing.append(SafetyCheck.FACTORY_BASELINE_EXISTS)
        except Exception:
            missing.append(SafetyCheck.BASELINE_INTEGRITY_VERIFIED)
        if not request.current_ecu_state_captured:
            missing.append(SafetyCheck.CURRENT_ECU_STATE_CAPTURED)
        if not request.proposed_change_validated:
            missing.append(SafetyCheck.PROPOSED_CHANGE_VALIDATED)
        if not request.power_communication_valid:
            missing.append(SafetyCheck.POWER_COMMUNICATION_VALID)
        if request.restore_level is None:
            missing.append(SafetyCheck.RESTORE_PATH_AVAILABLE)
        if not request.user_authorized:
            missing.append(SafetyCheck.USER_AUTHORIZATION)
        return SafetyGateResult(passed=not missing, missing_checks=tuple(missing))
