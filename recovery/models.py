"""Rollback and recovery planning models independent of active tuning workspace."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RecoveryAction(StrEnum):
    RESTORE_FACTORY = "restore_factory"
    RESTORE_PREVIOUS_TUNE = "restore_previous_tune"
    RESTORE_PREVIOUS_CODING = "restore_previous_coding"
    RESTORE_PREVIOUS_ECU_SOFTWARE = "restore_previous_ecu_software"
    RESTORE_PREVIOUS_VEHICLE_CONFIGURATION = "restore_previous_vehicle_configuration"
    RECOVER_INTERRUPTED_PROGRAMMING = "recover_interrupted_programming"


@dataclass(frozen=True)
class RecoveryPlan:
    action: RecoveryAction
    target_version: str
    independent_workspace: bool
    verification_steps: tuple[str, ...]
