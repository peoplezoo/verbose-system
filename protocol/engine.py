"""Protocol layer above physical hardware and below vehicle operations."""

from __future__ import annotations

from dataclasses import dataclass

from hardware.models import DiagnosticProtocol


@dataclass(frozen=True)
class ProtocolFrame:
    protocol: DiagnosticProtocol
    target: str
    payload: bytes


class ProtocolEngine:
    """Builds protocol frames independently of the selected physical adapter."""

    def uds_request(self, target: str, payload: bytes) -> ProtocolFrame:
        return ProtocolFrame(DiagnosticProtocol.UDS, target, payload)

    def kwp2000_request(self, target: str, payload: bytes) -> ProtocolFrame:
        return ProtocolFrame(DiagnosticProtocol.KWP2000, target, payload)

    def doip_request(self, target: str, payload: bytes) -> ProtocolFrame:
        return ProtocolFrame(DiagnosticProtocol.DOIP, target, payload)
