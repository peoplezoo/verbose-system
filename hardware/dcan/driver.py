"""D-CAN adapter facade."""

from hardware.models import DiagnosticProtocol
from hardware.operations import EcuOperation, EcuOperationName


def read_dtc(ecu_address: str) -> EcuOperation:
    return EcuOperation(EcuOperationName.READ_DTC, ecu_address, DiagnosticProtocol.UDS)
