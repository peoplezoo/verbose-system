"""Security primitives separating LLM permissions from physical ECU authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PrincipalKind(StrEnum):
    LLM = "llm"
    TECHNICIAN = "technician"
    SERVICE_ACCOUNT = "service_account"
    HARDWARE_DEVICE = "hardware_device"


class OperationPermission(StrEnum):
    READ_DATA = "read_data"
    RUN_NON_DESTRUCTIVE_TEST = "run_non_destructive_test"
    CLEAR_FAULTS = "clear_faults"
    CODING = "coding"
    CALIBRATION_WRITE = "calibration_write"
    ECU_PROGRAMMING = "ecu_programming"
    FACTORY_RESTORE = "factory_restore"


@dataclass(frozen=True)
class Principal:
    principal_id: str
    kind: PrincipalKind
    permissions: tuple[OperationPermission, ...]


def assert_llm_has_no_unrestricted_programming(principal: Principal) -> None:
    if principal.kind == PrincipalKind.LLM and OperationPermission.ECU_PROGRAMMING in principal.permissions:
        raise PermissionError("LLM permissions must not equal physical ECU programming authority")
