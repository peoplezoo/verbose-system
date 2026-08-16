from vehicle.interface import SimulatedBmwInterface


def test_v01_sequence_returns_structured_diagnostic_data():
    snapshot = SimulatedBmwInterface().collect_snapshot()

    assert snapshot.vehicle.vin == "WBA8E9G50JNU12345"
    assert [ecu.name for ecu in snapshot.ecus] == ["DME", "EGS", "BDC"]
    assert len(snapshot.faults) == 1
    assert snapshot.faults[0].code == "P0171"
    assert snapshot.faults[0].ecu_name == "DME"


def test_interface_requires_connection_for_direct_reads():
    interface = SimulatedBmwInterface()

    try:
        interface.identify_vehicle()
    except RuntimeError as exc:
        assert "not connected" in str(exc)
    else:
        raise AssertionError("direct reads must require an established connection")
