"""K-Line/KWP2000 legacy adapter facade."""

from hardware.models import DiagnosticProtocol
from hardware.operations import EcuOperation, EcuOperationName


def read_legacy_identifier(ecu_address: str) -> EcuOperation:
    return EcuOperation(EcuOperationName.READ_ECU_IDENTIFIER, ecu_address, DiagnosticProtocol.KWP2000)
