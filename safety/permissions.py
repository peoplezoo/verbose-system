"""Permission checks for deterministic diagnostic and simulation operations."""

from __future__ import annotations

from safety.readonly import ECU_WRITE_SERVICES, READ_ONLY_SERVICES, SIMULATION_ONLY_SERVICES


def require_readonly(operation: str) -> None:
    """Raise if an operation is outside the V0.1 read-only vehicle envelope."""

    if operation not in READ_ONLY_SERVICES:
        raise PermissionError(f"Operation is not allowed in read-only mode: {operation}")


def require_no_ecu_write(operation: str) -> None:
    """Raise if a calculation/simulation path attempts to write to an ECU."""

    if operation in ECU_WRITE_SERVICES:
        raise PermissionError(f"ECU write operation is isolated from simulation: {operation}")
    if operation not in READ_ONLY_SERVICES | SIMULATION_ONLY_SERVICES:
        raise PermissionError(f"Unknown operation is not allowed by default: {operation}")
