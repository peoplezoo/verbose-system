from architecture.roadmap import IMPLEMENTATION_ROADMAP, assert_read_only_foundation_before_writes
from agent.reasoning import TestSelectionOptimizer
from audit.models import AuditEvent, ReproducibilityContext
from experiment.engine import DiagnosticExperiment
from knowledge.graph import DtcNode, Provenance, ProvenanceKind
from security.models import OperationPermission, Principal, PrincipalKind, assert_llm_has_no_unrestricted_programming


def test_roadmap_keeps_read_only_foundation_before_write_capability():
    assert_read_only_foundation_before_writes()
    assert [stage.code for stage in IMPLEMENTATION_ROADMAP[:3]] == ["V0", "V1", "V2"]
    assert not any(stage.allows_ecu_writes for stage in IMPLEMENTATION_ROADMAP[:9])


def test_dtc_knowledge_node_carries_provenance_and_reasoning_links():
    dtc = DtcNode(
        code="P0171",
        ecu="DME",
        subsystem="fuel_air_metering",
        symptoms=("positive fuel trims",),
        possible_causes=("vacuum leak", "low fuel pressure"),
        measurements=("lambda", "rail_pressure"),
        test_procedures=("smoke_test", "pressure_decay_test"),
        related_dtcs=("P0174",),
        wiring_refs=("DME-X60001-pin-1",),
        components=("MAF", "fuel_pump"),
        repair_procedures=("repair_air_leak",),
        provenance=Provenance(ProvenanceKind.AI_INFERENCE, "unit-test"),
    )

    assert "pressure_decay_test" in dtc.test_procedures
    assert dtc.provenance.kind == ProvenanceKind.AI_INFERENCE


def test_optimizer_selects_information_gain_under_risk_threshold():
    tests = (
        DiagnosticExperiment("fuel pressure", "pressure low", "road_test", risk=0.8, cost=1.0, information_gain=10.0),
        DiagnosticExperiment("fuel pressure", "pressure decays", "static_decay", risk=0.2, cost=2.0, information_gain=9.0),
    )

    selected = TestSelectionOptimizer().select(tests, risk_threshold=0.5)

    assert selected.test == "static_decay"


def test_llm_permissions_do_not_equal_physical_ecu_permissions():
    principal = Principal("diagnostic-llm", PrincipalKind.LLM, (OperationPermission.READ_DATA,))
    assert_llm_has_no_unrestricted_programming(principal)

    unsafe = Principal("unsafe-llm", PrincipalKind.LLM, (OperationPermission.ECU_PROGRAMMING,))
    try:
        assert_llm_has_no_unrestricted_programming(unsafe)
    except PermissionError as exc:
        assert "LLM permissions" in str(exc)
    else:
        raise AssertionError("LLM must not have unrestricted programming authority")


def test_audit_event_contains_reproducibility_context():
    context = ReproducibilityContext(
        model="diagnostic-llm",
        model_version="test",
        system_prompt_version="v1",
        tool_versions={"pytest": "unit"},
        bmw_software_version="ISTA-sim",
        vehicle_state_hash="abc123",
        calculation_version="calc-v1",
        knowledge_base_version="kb-v1",
    )
    event = AuditEvent(
        event_id="evt-1",
        vehicle_id="vehicle-1",
        vin="WBA8E9G50JNU12345",
        ecu="DME",
        operator="tech",
        ai_model="diagnostic-llm",
        tool="read_dtc",
        request="read faults",
        result="P0171",
        before_state="state-1",
        after_state="state-1",
        authorization="read_data:auto",
        validation="read_only",
        reproducibility=context,
    )

    assert event.reproducibility.knowledge_base_version == "kb-v1"
