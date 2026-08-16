from hardware.models import DiagnosticProtocol, InterfaceFamily
from hardware.operations import EcuOperation, EcuOperationName, ProtocolRouter
from hardware.policy import HardwarePolicy
from hardware.registry import HardwareRegistry
from hardware.topology import DEFAULT_ZGW_TOPOLOGY


def test_registry_covers_bmw_relevant_interface_families_and_transports():
    registry = HardwareRegistry()

    assert registry.by_family(InterfaceFamily.OEM)
    assert registry.by_family(InterfaceFamily.PASS_THRU)
    assert registry.by_family(InterfaceFamily.DIRECT_BUS)
    assert registry.by_family(InterfaceFamily.MEASUREMENT)
    assert registry.get("icom").variants == ("ICOM Next A", "ICOM A", "ICOM A2", "ICOM B", "ICOM C")
    assert registry.get("measurement_bus").capability.notes


def test_protocol_router_keeps_operation_names_transport_independent():
    registry = HardwareRegistry()
    operation = EcuOperation(EcuOperationName.READ_ECU_IDENTIFIER, "0x12", DiagnosticProtocol.UDS)

    routed = ProtocolRouter().route(operation, registry.adapters)

    assert routed.operation.name == EcuOperationName.READ_ECU_IDENTIFIER
    assert routed.adapter.adapter_id in {"icom", "j2534", "kdcan", "native_can"}


def test_doip_can_route_over_enet_without_hard_coding_enet_operation_name():
    registry = HardwareRegistry()
    operation = EcuOperation(EcuOperationName.UDS_REQUEST, "0x12", DiagnosticProtocol.DOIP, b"\x22\xf1\x90")

    routed = ProtocolRouter().route(operation, (registry.get("enet"),))

    assert routed.adapter.adapter_id == "enet"
    assert routed.operation.name == EcuOperationName.UDS_REQUEST


def test_wireless_programming_is_rejected_by_policy():
    adapter = HardwareRegistry().get("j2534")

    try:
        HardwarePolicy().require_programming_authorized(adapter)
    except PermissionError as exc:
        assert "Wireless" in str(exc)
    else:
        raise AssertionError("wireless-capable J2534 links must not be auto-authorized for programming")


def test_bmw_can_network_variants_are_topology_not_adapter_names():
    topology = DEFAULT_ZGW_TOPOLOGY
    networks = {node.transport for node in topology.nodes}

    assert topology.gateway == "ZGW"
    assert any(str(network).endswith("pt_can") or getattr(network, "value", None) == "pt_can" for network in networks)
    assert any("DME" in node.modules for node in topology.nodes)
