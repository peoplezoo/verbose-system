"""Protocol-independent ECU operations routed over selected hardware."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from hardware.models import DiagnosticProtocol, HardwareAdapter


class EcuOperationName(StrEnum):
    READ_ECU_IDENTIFIER = "read_ecu_identifier"
    READ_DTC = "read_dtc"
    READ_MEASUREMENT = "read_measurement"
    UDS_REQUEST = "uds_request"
    EXECUTE_SERVICE = "execute_service"


@dataclass(frozen=True)
class EcuOperation:
    """Operation intent independent of ICOM/ENET/J2534/D-CAN/K-Line implementation."""

    name: EcuOperationName
    ecu_address: str
    protocol: DiagnosticProtocol
    payload: bytes = b""


@dataclass(frozen=True)
class RoutedOperation:
    """Operation plus the hardware selected to carry it."""

    operation: EcuOperation
    adapter: HardwareAdapter


class ProtocolRouter:
    """Selects transport-capable hardware without changing the ECU operation name."""

    def route(self, operation: EcuOperation, adapters: tuple[HardwareAdapter, ...]) -> RoutedOperation:
        for adapter in adapters:
            if operation.protocol in adapter.capability.protocols:
                return RoutedOperation(operation=operation, adapter=adapter)
        raise LookupError(f"No hardware adapter supports protocol: {operation.protocol}")
