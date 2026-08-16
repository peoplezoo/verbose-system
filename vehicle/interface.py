"""Deterministic vehicle communication boundary.

The LLM layer may decide what should be investigated, but only classes that
implement :class:`VehicleInterface` should access the vehicle. This keeps V0.1
read-only, testable, and replaceable with a hardware adapter later.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from vehicle.ecu import DiagnosticSnapshot, Ecu, FaultMemoryEntry, VehicleIdentification


class VehicleInterface(ABC):
    """Abstract read-only contract for BMW diagnostic communication."""

    @abstractmethod
    def connect(self) -> None:
        """Establish communication with the diagnostic interface."""

    @abstractmethod
    def identify_vehicle(self) -> VehicleIdentification:
        """Read and return the vehicle VIN/identity."""

    @abstractmethod
    def scan_ecus(self) -> list[Ecu]:
        """Enumerate reachable ECUs."""

    @abstractmethod
    def read_fault_memory(self, ecus: Iterable[Ecu] | None = None) -> list[FaultMemoryEntry]:
        """Read fault memory from the supplied ECUs or all discovered ECUs."""

    def collect_snapshot(self) -> DiagnosticSnapshot:
        """Run the V0.1 deterministic diagnostic sequence."""

        self.connect()
        vehicle = self.identify_vehicle()
        ecus = self.scan_ecus()
        faults = self.read_fault_memory(ecus)
        return DiagnosticSnapshot(vehicle=vehicle, ecus=ecus, faults=faults)


class SimulatedBmwInterface(VehicleInterface):
    """Deterministic simulator used until BMW hardware integration is added."""

    def __init__(
        self,
        vin: str = "WBA8E9G50JNU12345",
        ecus: list[Ecu] | None = None,
        faults: list[FaultMemoryEntry] | None = None,
    ) -> None:
        self._vin = vin
        self._ecus = ecus or [
            Ecu(address="0x12", name="DME", variant="B48", metadata={"bus": "PT-CAN"}),
            Ecu(address="0x18", name="EGS", variant="8HP", metadata={"bus": "PT-CAN"}),
            Ecu(address="0x40", name="BDC", variant="G-Series", metadata={"bus": "K-CAN"}),
        ]
        self._faults = faults or [
            FaultMemoryEntry(
                ecu_address="0x12",
                ecu_name="DME",
                code="P0171",
                description="System too lean, bank 1",
                status="stored",
                severity="medium",
            )
        ]
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def identify_vehicle(self) -> VehicleIdentification:
        self._require_connection()
        return VehicleIdentification(vin=self._vin)

    def scan_ecus(self) -> list[Ecu]:
        self._require_connection()
        return list(self._ecus)

    def read_fault_memory(self, ecus: Iterable[Ecu] | None = None) -> list[FaultMemoryEntry]:
        self._require_connection()
        if ecus is None:
            return list(self._faults)
        allowed_addresses = {ecu.address for ecu in ecus}
        return [fault for fault in self._faults if fault.ecu_address in allowed_addresses]

    def _require_connection(self) -> None:
        if not self.connected:
            raise RuntimeError("Vehicle interface is not connected")
