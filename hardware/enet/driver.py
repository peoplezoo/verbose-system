"""ENET driver facade for BMW Ethernet/DoIP operations."""

from hardware.models import DiagnosticProtocol
from hardware.operations import EcuOperation, EcuOperationName
from hardware.registry import HardwareRegistry


def discover_vehicle():
    return HardwareRegistry().get("enet")


def send_doip(ecu_address: str, payload: bytes) -> EcuOperation:
    return EcuOperation(EcuOperationName.UDS_REQUEST, ecu_address, DiagnosticProtocol.DOIP, payload)
