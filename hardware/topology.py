"""BMW bus-topology primitives."""

from __future__ import annotations

from dataclasses import dataclass

from hardware.models import BmwCanNetwork, PhysicalTransport


@dataclass(frozen=True)
class BusNode:
    name: str
    transport: PhysicalTransport | BmwCanNetwork
    modules: tuple[str, ...]


@dataclass(frozen=True)
class BmwBusTopology:
    gateway: str
    nodes: tuple[BusNode, ...]


DEFAULT_ZGW_TOPOLOGY = BmwBusTopology(
    gateway="ZGW",
    nodes=(
        BusNode("powertrain", BmwCanNetwork.PT_CAN, ("DME", "EGS")),
        BusNode("chassis", BmwCanNetwork.F_CAN, ("DSC", "EPS")),
        BusNode("body", BmwCanNetwork.K_CAN, ("FEM", "BDC")),
        BusNode("flexray", PhysicalTransport.FLEXRAY, ("chassis",)),
        BusNode("ethernet", PhysicalTransport.ETHERNET, ("DoIP",)),
    ),
)
