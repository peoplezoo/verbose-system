"""Registry of BMW-relevant hardware adapters and physical transports."""

from __future__ import annotations

from hardware.models import (
    BmwCanNetwork,
    DiagnosticProtocol,
    HardwareAdapter,
    HardwareCapability,
    InterfaceFamily,
    LinkPolicy,
    PhysicalTransport,
)


class HardwareRegistry:
    """Normalized catalog for OEM, pass-thru, direct-bus, host, and measurement hardware."""

    DEFAULTS = (
        HardwareAdapter(
            adapter_id="icom",
            name="ICOM family",
            family=InterfaceFamily.OEM,
            variants=("ICOM Next A", "ICOM A", "ICOM A2", "ICOM B", "ICOM C"),
            host_transports=(PhysicalTransport.ETHERNET, PhysicalTransport.WIFI),
            capability=HardwareCapability(
                transports=(PhysicalTransport.ETHERNET, PhysicalTransport.D_CAN, PhysicalTransport.K_LINE, PhysicalTransport.MOST),
                protocols=(DiagnosticProtocol.UDS, DiagnosticProtocol.KWP2000, DiagnosticProtocol.DOIP, DiagnosticProtocol.ISO_TP),
                policies=(LinkPolicy.READ_ONLY, LinkPolicy.PROGRAMMING_CAPABLE),
            ),
        ),
        HardwareAdapter(
            adapter_id="enet",
            name="ENET",
            family=InterfaceFamily.OEM,
            host_transports=(PhysicalTransport.ETHERNET,),
            capability=HardwareCapability(
                transports=(PhysicalTransport.ETHERNET, PhysicalTransport.AUTOMOTIVE_ETHERNET_100BASE_TX),
                protocols=(DiagnosticProtocol.DOIP, DiagnosticProtocol.HSFZ, DiagnosticProtocol.UDS),
                policies=(LinkPolicy.READ_ONLY,),
            ),
        ),
        HardwareAdapter(
            adapter_id="j2534",
            name="SAE J2534 Pass-Thru VCI",
            family=InterfaceFamily.PASS_THRU,
            host_transports=(PhysicalTransport.USB, PhysicalTransport.ETHERNET, PhysicalTransport.WIFI),
            capability=HardwareCapability(
                transports=(PhysicalTransport.CAN, PhysicalTransport.D_CAN, PhysicalTransport.K_LINE),
                protocols=(DiagnosticProtocol.UDS, DiagnosticProtocol.KWP2000, DiagnosticProtocol.ISO_9141, DiagnosticProtocol.ISO_14230, DiagnosticProtocol.ISO_15765),
                policies=(LinkPolicy.READ_ONLY, LinkPolicy.PROGRAMMING_CAPABLE),
            ),
        ),
        HardwareAdapter(
            adapter_id="kdcan",
            name="K+DCAN USB adapter",
            family=InterfaceFamily.PASS_THRU,
            host_transports=(PhysicalTransport.USB,),
            capability=HardwareCapability(
                transports=(PhysicalTransport.K_LINE, PhysicalTransport.D_CAN),
                protocols=(DiagnosticProtocol.KWP2000, DiagnosticProtocol.DS2, DiagnosticProtocol.UDS, DiagnosticProtocol.ISO_TP),
                policies=(LinkPolicy.READ_ONLY,),
            ),
        ),
        HardwareAdapter(
            adapter_id="native_can",
            name="Native CAN subsystem",
            family=InterfaceFamily.DIRECT_BUS,
            host_transports=(PhysicalTransport.USB,),
            capability=HardwareCapability(
                transports=(PhysicalTransport.CAN,),
                protocols=(DiagnosticProtocol.CAN_RAW, DiagnosticProtocol.ISO_TP, DiagnosticProtocol.UDS),
                policies=(LinkPolicy.READ_ONLY,),
                bmw_networks=(
                    BmwCanNetwork.PT_CAN,
                    BmwCanNetwork.PT_CAN2,
                    BmwCanNetwork.F_CAN,
                    BmwCanNetwork.K_CAN,
                    BmwCanNetwork.K_CAN2,
                    BmwCanNetwork.LOCAL_CAN,
                    BmwCanNetwork.D_CAN,
                ),
            ),
        ),
        HardwareAdapter(
            adapter_id="direct_buses",
            name="Direct BMW bus interfaces",
            family=InterfaceFamily.DIRECT_BUS,
            capability=HardwareCapability(
                transports=(PhysicalTransport.LIN, PhysicalTransport.FLEXRAY, PhysicalTransport.BSD, PhysicalTransport.BYTEFLIGHT, PhysicalTransport.K_BUS, PhysicalTransport.I_BUS, PhysicalTransport.MOST),
                protocols=(DiagnosticProtocol.LIN_RAW, DiagnosticProtocol.FLEXRAY_RAW),
                policies=(LinkPolicy.READ_ONLY,),
            ),
        ),
        HardwareAdapter(
            adapter_id="measurement_bus",
            name="Measurement hardware",
            family=InterfaceFamily.MEASUREMENT,
            host_transports=(PhysicalTransport.USB, PhysicalTransport.ETHERNET, PhysicalTransport.BLUETOOTH),
            capability=HardwareCapability(
                transports=(PhysicalTransport.USB, PhysicalTransport.ETHERNET),
                protocols=(),
                policies=(LinkPolicy.MEASUREMENT_ONLY,),
                notes="Oscilloscope, logic analyzer, current/voltage/pressure/temperature sensors, wideband lambda, CAN/Ethernet analyzer, IMU, dyno.",
            ),
        ),
    )

    def __init__(self, adapters: tuple[HardwareAdapter, ...] = DEFAULTS) -> None:
        self.adapters = adapters

    def by_family(self, family: InterfaceFamily) -> tuple[HardwareAdapter, ...]:
        return tuple(adapter for adapter in self.adapters if adapter.family == family)

    def supporting_protocol(self, protocol: DiagnosticProtocol) -> tuple[HardwareAdapter, ...]:
        return tuple(adapter for adapter in self.adapters if protocol in adapter.capability.protocols)

    def get(self, adapter_id: str) -> HardwareAdapter:
        return next(adapter for adapter in self.adapters if adapter.adapter_id == adapter_id)
