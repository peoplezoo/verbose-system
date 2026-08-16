"""Hardware abstraction models for BMW-relevant transports and interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class InterfaceFamily(StrEnum):
    OEM = "oem_interface"
    PASS_THRU = "pass_thru_vci"
    DIRECT_BUS = "direct_bus"
    HOST_TRANSPORT = "host_transport"
    MEASUREMENT = "measurement"


class PhysicalTransport(StrEnum):
    ETHERNET = "ethernet"
    USB = "usb"
    SERIAL = "serial"
    WIFI = "wifi"
    BLUETOOTH = "bluetooth"
    BLUETOOTH_LE = "bluetooth_le"
    CAN = "can"
    D_CAN = "d_can"
    K_LINE = "k_line"
    LIN = "lin"
    FLEXRAY = "flexray"
    MOST = "most"
    BSD = "bsd"
    BYTEFLIGHT = "byteflight"
    K_BUS = "k_bus"
    I_BUS = "i_bus"
    AUTOMOTIVE_ETHERNET_100BASE_TX = "100base_tx"
    AUTOMOTIVE_ETHERNET_100BASE_T1 = "100base_t1"
    AUTOMOTIVE_ETHERNET_1000BASE_T1 = "1000base_t1"


class DiagnosticProtocol(StrEnum):
    UDS = "uds"
    KWP2000 = "kwp2000"
    DS2 = "bmw_ds2"
    ISO_9141 = "iso9141"
    ISO_14230 = "iso14230"
    ISO_15765 = "iso15765"
    ISO_TP = "isotp"
    DOIP = "doip"
    HSFZ = "bmw_hsfz"
    CAN_RAW = "can_raw"
    LIN_RAW = "lin_raw"
    FLEXRAY_RAW = "flexray_raw"
    ETHERNET_RAW = "ethernet_raw"


class BmwCanNetwork(StrEnum):
    PT_CAN = "pt_can"
    PT_CAN2 = "pt_can2"
    F_CAN = "f_can"
    K_CAN = "k_can"
    K_CAN2 = "k_can2"
    LOCAL_CAN = "local_can"
    D_CAN = "d_can"


class LinkPolicy(StrEnum):
    READ_ONLY = "read_only"
    PROGRAMMING_CAPABLE = "programming_capable"
    MEASUREMENT_ONLY = "measurement_only"


@dataclass(frozen=True)
class HardwareCapability:
    """Normalized capability exposed by an adapter regardless of vendor."""

    transports: tuple[PhysicalTransport, ...]
    protocols: tuple[DiagnosticProtocol, ...]
    policies: tuple[LinkPolicy, ...]
    bmw_networks: tuple[BmwCanNetwork, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class HardwareAdapter:
    """Physical adapter class discovered by the hardware abstraction layer."""

    adapter_id: str
    name: str
    family: InterfaceFamily
    capability: HardwareCapability
    variants: tuple[str, ...] = ()
    vendor: str | None = None
    host_transports: tuple[PhysicalTransport, ...] = field(default_factory=tuple)

    @property
    def supports_programming(self) -> bool:
        return LinkPolicy.PROGRAMMING_CAPABLE in self.capability.policies

    @property
    def is_wireless(self) -> bool:
        wireless = {PhysicalTransport.WIFI, PhysicalTransport.BLUETOOTH, PhysicalTransport.BLUETOOTH_LE}
        return bool(wireless.intersection(self.host_transports))
