from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

from ev4_transition.canonical_json import bytes_sha256, canonical_sha256
from ev4_transition.contract_source import LocalCheckoutContractSource
from ev4_transition.final_gate_authority import is_authoritative_final_gate_result
from ev4_transition.kernel_decision_dependencies import EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES, KERNEL_ACCEPTED_COMMIT, KERNEL_INTAKE_RESULT_SCHEMA_ID, KERNEL_INTAKE_SCHEMA_ID, KERNEL_LOCK_SCHEMA_VERSION, KERNEL_REPOSITORY
from ev4_transition.kernel_decision_intake import KernelAuditExecution
from ev4_transition.transitions.final_gate import EXPECTED_FINAL_GATE_DEPENDENCIES, GATE_ID, PG_REPO, RESPONSIVE_OUTPUT_SCHEMA, RESPONSIVE_REPO, FinalGateConfig, run_final_gate, verify_final_gate_lock

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "fixtures/kernel-decision-intake/complete-layout-structure.synthetic.json"
ZERO_HASH = "0" * 64


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _lineage() -> dict:
    return {"decision_family":"layout_structure","decision_card_ref":"projection:test","selected_option":"flexbox","rejected_options":["grid"],"evidence_refs":["EV1"],"evidence_state":"validated","consumer_stage":"final_evidence_gate"}


def _raw_intake() -> dict:
    bundle = json.loads(BASE.read_text())
    bundle["synthetic"] = False
    bundle["produced_by"]["ref"] = "test-head"
    bundle["evidence"][0]["source"] = {"type":"repo_path","reference":"exports/project.json"}
    packet = bundle["payload"]["data"]["decision_packets"][0]
    for carrier in (packet["decision_record"], packet["resolver_input"]):
        carrier["evidence_refs"][0]["source_type"] = "project_export"
        carrier["evidence_refs"][0]["ref"] = "exports/project.json"
    return bundle


def _output(include_lineage: bool = True) -> dict:
    output = {"schema":RESPONSIVE_OUTPUT_SCHEMA,"responsive_tree_output":{"mode":"blocked"},"real_evidence":True,"evidence_status":"real"}
    if include_lineage:
        output["decision_lineage"] = _lineage()
    return output


def _pass(_: dict) -> KernelAuditExecution:
    return KernelAuditExecution("completed", {"audit_status":"pass","human_override_observed":False,"resolver_output":{"resolver_status":"auto_resolved","rule_id":"resolver.rule.layout_structure.mvp.v0","rule_version":"0.1.0"},"diagnostics":[]}, {"exit_code":0})


def _fail(_: dict) -> KernelAuditExecution:
    return KernelAuditExecution("completed", {"audit_status":"fail","human_override_observed":False,"resolver_output":{"resolver_status":"auto_resolved"},"diagnostics":[{"code":"L2_SELECTED_OPTION_RESOLVER_MISMATCH","severity":"error","source":"semantic","path":"decision_record.selected_option","message":"synthetic"}]}, {"exit_code":0})


def _repos(tmp_path: Path):
    pg, responsive, kernel = tmp_path / "pg", tmp_path / "responsive", tmp_path / "kernel"
    for dep in EXPECTED_FINAL_GATE_DEPENDENCIES.values():
        root = pg if dep.repository == PG_REPO else responsive
        if dep.path.endswith(".py"):
            text = "import sys\nprint('responsive ok')\nsys.exit(0)\n"
        elif dep.path.endswith(".json") and "responsive-output" in dep.path:
            text = json.dumps({"id":dep.contract_or_schema_id,"marker":dep.identity_marker,"$schema":"https://json-schema.org/draft/2020-12/schema","type":"object","required":["schema"],"properties":{"schema":{"const":RESPONSIVE_OUTPUT_SCHEMA}},"additionalProperties":True})
        elif dep.path.endswith(".json"):
            text = json.dumps({"id":dep.contract_or_schema_id,"marker":dep.identity_marker})
        else:
            text = f"{dep.identity_marker}\n"
        _write(root / dep.path, text)
    final_lock = {"schema_version":"final-gate-lock.v1","gate_id":GATE_ID,"files":[]}
    for dep in EXPECTED_FINAL_GATE_DEPENDENCIES.values():
        root = pg if dep.repository == PG_REPO else responsive
        final_lock["files"].append({"role":dep.role,"repository":dep.repository,"accepted_commit":dep.accepted_commit,"path":dep.path,"contract_or_schema_id":dep.contract_or_schema_id,"sha256_file_bytes":bytes_sha256((root/dep.path).read_bytes())})

    texts = {
        "decision_record_schema": json.dumps({"$id":"https://ev4.local/schemas/decision-record.v2.schema.json"}),
        "p0_decision_matrices": json.dumps({"matrix_registry_id":"p0-decision-matrices.v0","matrices":[{"decision_family_id":"layout_structure"}]}),
        "resolver_rule_registry": json.dumps({"registry_id":"resolver-rule-registry.v0","active_rules":[{"decision_family_id":"layout_structure"}]}),
        "layout_structure_rule": json.dumps({"contract_id":"resolver.contract.layout_structure.mvp.v0","rule_id":"resolver.rule.layout_structure.mvp.v0","rule_version":"0.1.0"}),
        "resolver_implementation": "export function resolveDecision() {}\n",
        "l2_decision_correctness_audit": "export function auditDecisionRecord() {}\n",
    }
    files = []
    for role, dep in EXPECTED_KERNEL_SEMANTIC_DEPENDENCIES.items():
        _write(kernel / dep.path, texts[role])
        files.append({"role":role,"repository":dep.repository,"accepted_commit":dep.accepted_commit,"path":dep.path,"contract_or_schema_id":dep.contract_or_schema_id,"sha256_file_bytes":bytes_sha256((kernel/dep.path).read_bytes())})
    kernel_lock = {"schema_version":KERNEL_LOCK_SCHEMA_VERSION,"intake_schema_id":KERNEL_INTAKE_SCHEMA_ID,"kernel_pin":{"repository":KERNEL_REPOSITORY,"accepted_commit":KERNEL_ACCEPTED_COMMIT},"files":sorted(files,key=lambda item:item["role"])}
    source = LocalCheckoutContractSource({PG_REPO:pg, RESPONSIVE_REPO:responsive, KERNEL_REPOSITORY:kernel})
    return pg, responsive, kernel, source, final_lock, kernel_lock


def _run(tmp_path: Path, value: dict, *, executor=_pass):
    pg, responsive, kernel, source, final_lock, kernel_lock = _repos(tmp_path)
    calls: list[dict] = []
    def counted(packet: dict) -> KernelAuditExecution:
        calls.append(packet)
        return executor(packet)
    config = FinalGateConfig(
        schema_root=ROOT/"schemas",
        lock=final_lock,
        project_gate_repo_root=pg,
        responsive_repo_root=responsive,
        timeout_seconds=30,
        require_real_evidence=True,
        kernel_intake_lock=kernel_lock,
        kernel_repo_root=kernel,
        kernel_audit_executor=counted,
    )
    return run_final_gate(value, source, config), calls, kernel_lock


def _input(*, include_raw: bool = True, include_lineage: bool = True) -> dict:
    value = {"responsive_output":_output(include_lineage)}
    if include_raw:
        value["kernel_decision_intake"] = _raw_intake()
    return value


def _forged_result(kernel_lock: dict) -> dict:
    lock_hash = canonical_sha256(kernel_lock)
    evidence = {"evidence_id":"EV1","source_type":"project_export","reference":"exports/project.json"}
    hash_record = lambda scope: {"algorithm":"sha256","scope":scope,"value":ZERO_HASH}
    return {
        "schema_version":KERNEL_INTAKE_RESULT_SCHEMA_ID,
        "result_type":"kernel_decision_intake",
        "status":"accepted",
        "kernel_pin":{"repository":KERNEL_REPOSITORY,"accepted_commit":KERNEL_ACCEPTED_COMMIT,"semantic_lock_sha256":lock_hash},
        "accepted_requires":{"kernel_pin_verified":True,"semantic_lock_verified":True,"intake_schema_valid":True,"packet_binding_valid":True,"l2_executed_all":True,"no_unsupported_claims":True,"result_schema_valid":True},
        "diagnostics":[],
        "upstream_diagnostics":[{"packet_id":"P1","diagnostics":[]}],
        "packet_results":[{
            "packet_id":"P1","decision_id":"D1","decision_family_id":"layout_structure","status":"accepted","l2_executed":True,"human_override_observed":False,
            "project_gate_diagnostics":[],"upstream_diagnostics":[],"resolver_output":{"resolver_status":"auto_resolved"},
            "decision_record_ref":{"packet_id":"P1","decision_id":"D1","sha256":ZERO_HASH},
            "source_evidence_refs":[evidence],"runtime_evidence_refs":[],
            "hashes":{"packet_hash":hash_record("packet"),"decision_record_hash":hash_record("decision_record"),"resolver_input_hash":hash_record("resolver_input"),"audit_context_hash":hash_record("audit_context")},
            "provenance":{"provenance_id":"FORGED"},"execution_record":{"tool_kind":"validator","exit_code":0,"owner_repo":KERNEL_REPOSITORY,"owner_commit":KERNEL_ACCEPTED_COMMIT}
        }],
        "derived_counts":{"provisional_count":0,"human_override_count":0,"unresolved_decision_count":0,"accepted_decision_count":1,"rejected_decision_count":0},
        "decision_record_refs":[{"packet_id":"P1","decision_id":"D1","sha256":ZERO_HASH}],
        "source_evidence_refs":[{"packet_id":"P1",**evidence}],
        "runtime_evidence_refs":[],
        "hashes":{"source_input_hash":hash_record("source_input"),"semantic_lock_hash":{"algorithm":"sha256","scope":"semantic_lock","value":lock_hash}},
        "provenance":{"source_bundle_id":"forged","source_bundle_provenance":{"source":"attacker"},"result_producer":PG_REPO}
    }


def _codes(result: dict) -> list[str]:
    return [item["code"] for item in result["diagnostics"]]


def test_final_gate_executes_raw_intake_and_accepts_only_internal_result(tmp_path: Path):
    result, calls, _ = _run(tmp_path, _input())
    assert result["status"] == "accepted", result
    assert len(calls) == 1
    assert result["accepted_requires"]["kernel_decision_intake_accepted"] is True
    assert result["kernel_decision_intake_result"]["status"] == "accepted"
    assert result["output"]["decision_lineage"] == _lineage()
    assert is_authoritative_final_gate_result(result)


def test_precomputed_result_without_raw_intake_cannot_authenticate(tmp_path: Path):
    value = _input(include_raw=False)
    _, _, _, _, _, kernel_lock = _repos(tmp_path)
    value["kernel_decision_intake_result"] = _forged_result(kernel_lock)
    result, calls, _ = _run(tmp_path / "run", value)
    assert result["status"] == "invalid"
    assert calls == []
    assert result["accepted_requires"]["kernel_decision_intake_accepted"] is False
    assert "PG.FINAL.KERNEL_INTAKE_REQUIRED" in _codes(result)


def test_forged_schema_valid_result_cannot_replace_internal_execution(tmp_path: Path):
    value = _input()
    _, _, _, _, _, kernel_lock = _repos(tmp_path)
    forged = _forged_result(kernel_lock)
    schema = json.loads((ROOT/"schemas/kernel-decision-intake-result/kernel-decision-intake-result.v1.schema.json").read_text())
    Draft202012Validator(schema).validate(forged)
    value["kernel_decision_intake_result"] = forged
    result, calls, _ = _run(tmp_path / "run", value)
    assert len(calls) == 1
    assert result["status"] == "invalid"
    assert result["accepted_requires"]["kernel_decision_intake_accepted"] is False
    assert "PG.FINAL.KERNEL_INTAKE_PROJECTION_MISMATCH" in _codes(result)
    assert result["kernel_decision_intake_result"] != forged


def test_supplied_projection_differing_from_recomputed_result_fails_closed(tmp_path: Path):
    value = _input()
    result_without_projection, calls, _ = _run(tmp_path / "first", deepcopy(value))
    assert len(calls) == 1
    supplied = dict(result_without_projection["kernel_decision_intake_result"])
    supplied["derived_counts"] = {**supplied["derived_counts"], "accepted_decision_count": 99}
    value["kernel_decision_intake_result"] = supplied
    result, calls, _ = _run(tmp_path / "second", value)
    assert len(calls) == 1
    assert result["status"] == "invalid"
    assert "PG.FINAL.KERNEL_INTAKE_PROJECTION_MISMATCH" in _codes(result)


def test_raw_intake_with_kernel_execution_unavailable_is_insufficient(tmp_path: Path):
    result, calls, _ = _run(tmp_path, _input(), executor=lambda _: KernelAuditExecution("unavailable", None))
    assert len(calls) == 1
    assert result["status"] == "insufficient_evidence"
    assert result["accepted_requires"]["kernel_decision_intake_accepted"] is False
    assert "PG.FINAL.KERNEL_INTAKE_NOT_ACCEPTED" in _codes(result)


def test_raw_intake_with_nonaccepted_internal_result_is_invalid(tmp_path: Path):
    result, calls, _ = _run(tmp_path, _input(), executor=_fail)
    assert len(calls) == 1
    assert result["status"] == "invalid"
    assert result["kernel_decision_intake_result"]["status"] == "invalid"
    assert "PG.FINAL.KERNEL_INTAKE_NOT_ACCEPTED" in _codes(result)


def test_complete_lineage_alone_cannot_authenticate_acceptance(tmp_path: Path):
    result, calls, _ = _run(tmp_path, _input(include_raw=False, include_lineage=True))
    assert calls == []
    assert result["status"] == "invalid"
    assert "PG.FINAL.KERNEL_INTAKE_REQUIRED" in _codes(result)


def test_lineage_is_optional_projection_when_internal_intake_is_authoritative(tmp_path: Path):
    result, calls, _ = _run(tmp_path, _input(include_lineage=False))
    assert len(calls) == 1
    assert result["status"] == "accepted", result
    assert result["accepted_requires"]["decision_lineage_projection_valid"] is True


def test_final_gate_rejects_lineage_projection_drift(tmp_path: Path):
    value = _input()
    value["decision_lineage"] = {**_lineage(), "selected_option":"grid"}
    result, calls, _ = _run(tmp_path, value)
    assert len(calls) == 1
    assert result["status"] == "invalid"
    assert "PG.FINAL.DECISION_LINEAGE_DRIFT" in _codes(result)


def test_final_gate_rejects_forbidden_claim(tmp_path: Path):
    value = _input()
    value["claim"] = "production_ready"
    result, calls, _ = _run(tmp_path, value)
    assert len(calls) == 1
    assert result["status"] == "invalid"
    assert "PG.FINAL.FORBIDDEN_CLAIM" in _codes(result)


def test_final_gate_does_not_count_synthetic_as_real_evidence(tmp_path: Path):
    value = _input()
    value["responsive_output"]["synthetic_only"] = True
    value["responsive_output"]["evidence_status"] = "synthetic_fixture"
    result, calls, _ = _run(tmp_path, value)
    assert len(calls) == 1
    assert result["status"] == "insufficient_evidence"
    assert "PG.FINAL.SYNTHETIC_ONLY_EVIDENCE" in _codes(result)


def test_final_gate_lock_detects_hash_mismatch(tmp_path: Path):
    _, _, _, source, final_lock, _ = _repos(tmp_path)
    final_lock["files"][0]["sha256_file_bytes"] = "0"*64
    assert any(item.code == "PG.FINAL.EXTERNAL_HASH_MISMATCH" for item in verify_final_gate_lock(final_lock, source))


def test_final_gate_completed_result_is_schema_valid(tmp_path: Path):
    result, _, _ = _run(tmp_path, _input())
    schema = json.loads((ROOT/"schemas/final-gate-result/final-gate-result.v1.schema.json").read_text())
    Draft202012Validator(schema).validate(result)
