from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

from ev4_transition.canonical_json import bytes_sha256, canonical_sha256, load_json_file
from ev4_transition.contract_source import ContractSource, LocalCheckoutContractSource
from ev4_transition.diagnostics import Diagnostic, diagnostic, sort_diagnostics
from ev4_transition.runners.kernel_intake import KernelAuditExecution, execute_kernel_l2_audit

KERNEL_REPOSITORY = "rezahh107/EV4-Decision-Kernel"
KERNEL_COMMIT = "76a82e28543ff8f0babca11b7d7dccac96b92894"
INTAKE_SCHEMA_ID = "ev4-project-gate-kernel-decision-intake@1.0.0"
RESULT_SCHEMA_VERSION = "kernel-decision-intake-result.v1"
LOCK_ID = "kroad-011-kernel-semantic-lock.v1"
FORBIDDEN_AUTHORED_FIELDS = {"l2_audit_status", "resolver_output", "audit_passed", "kernel_validated", "accepted_decision_count", "rejected_decision_count", "provisional_count", "human_override_count", "unresolved_decision_count", "resolved", "accepted"}
UNSUPPORTED_ASSERTED_CLAIMS = {"builder_execution_proof", "builder_ready", "runtime_validated", "browser_validated", "downstream_enforced", "project_gate_accepted", "release_ready", "production_ready", "frontend_correctness", "responsive_correctness"}
_STATUS_RANK = {"accepted": 0, "repair_needed": 1, "insufficient_evidence": 2, "invalid": 3}


@dataclass(frozen=True)
class KernelIntakeConfig:
    schema_root: Path
    dependency_config: dict[str, Any]
    semantic_lock: dict[str, Any]
    kernel_repo_root: Path | None
    bridge_path: Path
    timeout_seconds: float = 30
    executor: Callable[..., KernelAuditExecution] = execute_kernel_l2_audit


def kernel_decision_intake_from_local_paths(bundle: Any, *, schema_root: str | Path, dependency_config_path: str | Path, semantic_lock_path: str | Path, kernel_repo: str | Path, bridge_path: str | Path, timeout_seconds: float = 30) -> dict[str, Any]:
    expected = load_json_file(dependency_config_path)
    lock = load_json_file(semantic_lock_path)
    source = LocalCheckoutContractSource({KERNEL_REPOSITORY: Path(kernel_repo)})
    config = KernelIntakeConfig(Path(schema_root), expected, lock, Path(kernel_repo), Path(bridge_path), timeout_seconds)
    return run_kernel_decision_intake(bundle, source, config)


def verify_kernel_semantic_lock(lock: Any, expected: Any, source: ContractSource) -> list[Diagnostic]:
    if not isinstance(expected, dict) or not isinstance(expected.get("dependencies"), list):
        return [diagnostic("PG.KERNEL.EXPECTED_CONFIG_INVALID", "error", "Project Gate dependency configuration is invalid.", "$.dependency_config")]
    if not isinstance(lock, dict):
        return [diagnostic("PG.KERNEL.LOCK_NOT_OBJECT", "error", "Kernel semantic lock must be an object.", "$.kernel_pin")]
    out: list[Diagnostic] = []
    if lock.get("schema_version") != "kernel-decision-intake-semantic-lock.v1" or lock.get("lock_id") != LOCK_ID:
        out.append(diagnostic("PG.KERNEL.LOCK_IDENTITY_MISMATCH", "error", "Kernel semantic lock identity is invalid.", "$.kernel_pin.semantic_lock_id"))
    entries = lock.get("files")
    if not isinstance(entries, list):
        return sort_diagnostics([*out, diagnostic("PG.KERNEL.LOCK_FILES_INVALID", "error", "Kernel semantic lock files must be an array.", "$.kernel_pin")])
    expected_by_role = {item["role"]: item for item in expected["dependencies"] if isinstance(item, dict) and "role" in item}
    actual_by_role = {item.get("role"): item for item in entries if isinstance(item, dict)}
    if len(entries) != len(expected_by_role) or set(actual_by_role) != set(expected_by_role):
        out.append(diagnostic("PG.KERNEL.LOCK_DEPENDENCY_SET_MISMATCH", "error", "Semantic lock must contain exactly the approved dependency roles.", "$.kernel_pin"))
    for role, spec in expected_by_role.items():
        item = actual_by_role.get(role)
        path = f"$.kernel_pin.lock.files[{role}]"
        if not isinstance(item, dict):
            continue
        for field, value in (("repository", expected.get("repository")), ("accepted_commit", expected.get("accepted_commit")), ("path", spec.get("path"))):
            if item.get(field) != value:
                out.append(diagnostic("PG.KERNEL.LOCK_METADATA_MISMATCH", "error", "Semantic lock metadata does not match Project Gate configuration.", f"{path}.{field}", role=role))
        try:
            raw = source.read_bytes(expected["repository"], expected["accepted_commit"], spec["path"])
        except Exception as exc:
            out.append(diagnostic("PG.KERNEL.CHECKOUT_UNAVAILABLE", "insufficient_evidence", "Pinned Kernel artifact could not be read.", path, role=role, error_type=type(exc).__name__))
            continue
        if item.get("sha256_file_bytes") != bytes_sha256(raw):
            out.append(diagnostic("PG.KERNEL.ARTIFACT_HASH_MISMATCH", "error", "Pinned Kernel artifact hash does not match the semantic lock.", path, role=role))
        identity = spec.get("identity", {})
        text = raw.decode("utf-8", errors="replace")
        wanted = identity.get("contains", identity.get("value"))
        if "contains" in identity:
            observed = wanted if wanted in text else None
        else:
            try:
                parsed = json.loads(text)
                observed = parsed.get(identity.get("field")) if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                observed = None
        if observed != wanted or item.get("identity") != wanted:
            out.append(diagnostic("PG.KERNEL.ARTIFACT_IDENTITY_MISMATCH", "error", "Pinned Kernel artifact identity does not match Project Gate configuration.", path, role=role))
    return sort_diagnostics(out)


def run_kernel_decision_intake(bundle: Any, source: ContractSource, config: KernelIntakeConfig) -> dict[str, Any]:
    diags: list[Diagnostic] = []
    req = {"stage_bundle_valid": False, "intake_schema_valid": False, "semantic_lock_verified": False, "kernel_l2_executed": False, "packet_binding_valid": False, "no_unsupported_claims": False, "result_schema_valid": True}
    stage_schema = load_json_file(config.schema_root / "stage-bundle" / "stage-bundle.v1.schema.json")
    stage_diags = _schema_diags(stage_schema, bundle, "PG.KERNEL.STAGE_BUNDLE_SCHEMA_INVALID")
    diags.extend(stage_diags)
    req["stage_bundle_valid"] = not stage_diags

    intake = None
    if isinstance(bundle, dict) and isinstance(bundle.get("payload"), dict):
        payload = bundle["payload"]
        if payload.get("schema_id") == INTAKE_SCHEMA_ID and isinstance(payload.get("data"), dict):
            intake = payload["data"]
        else:
            diags.append(diagnostic("PG.KERNEL.INTAKE_SCHEMA_UNKNOWN", "error", "Stage bundle payload schema is not the approved Kernel decision intake contract.", "$.payload.schema_id"))
    else:
        diags.append(diagnostic("PG.KERNEL.INTAKE_SCHEMA_UNKNOWN", "error", "Stage bundle payload schema is not the approved Kernel decision intake contract.", "$.payload.schema_id"))

    if intake is not None:
        intake_schema = load_json_file(config.schema_root / "kernel-decision-intake" / "kernel-decision-intake.v1.schema.json")
        intake_diags = _schema_diags(intake_schema, intake, "PG.KERNEL.INTAKE_SCHEMA_INVALID", "$.payload.data")
        diags.extend(intake_diags)
        req["intake_schema_valid"] = not intake_diags
        pin = intake.get("kernel_pin", {})
        for field, value in (("repository", config.dependency_config.get("repository")), ("accepted_commit", config.dependency_config.get("accepted_commit")), ("semantic_lock_id", LOCK_ID)):
            if pin.get(field) != value:
                diags.append(diagnostic("PG.KERNEL.PIN_MISMATCH", "error", "Intake Kernel pin does not match Project Gate configuration.", f"$.payload.data.kernel_pin.{field}", expected=value, actual=pin.get(field)))

    lock_diags = verify_kernel_semantic_lock(config.semantic_lock, config.dependency_config, source)
    diags.extend(lock_diags)
    req["semantic_lock_verified"] = not any(item.severity in {"error", "insufficient_evidence"} for item in lock_diags)

    forbidden = _find_keys(bundle, FORBIDDEN_AUTHORED_FIELDS)
    for path, field in forbidden:
        diags.append(diagnostic("PG.KERNEL.AUTHORED_DERIVED_FIELD_FORBIDDEN", "error", "Derived Kernel or Project Gate output fields may not be authored in intake.", path, field=field))
    unsupported = _find_claims(bundle)
    for path, claim in unsupported:
        diags.append(diagnostic("PG.KERNEL.UNSUPPORTED_ASSERTED_CLAIM", "error", "The intake contains an unsupported assertion.", path, claim=claim))
    req["no_unsupported_claims"] = not unsupported

    packets = intake.get("decision_packets", []) if isinstance(intake, dict) else []
    binding = _binding_diags(packets) if isinstance(packets, list) else []
    diags.extend(binding)
    req["packet_binding_valid"] = not binding
    can_run = intake is not None and all(req[key] for key in ("stage_bundle_valid", "intake_schema_valid", "semantic_lock_verified", "packet_binding_valid", "no_unsupported_claims")) and not forbidden

    packet_results: list[dict[str, Any]] = []
    upstream: list[dict[str, Any]] = []
    if can_run:
        for index, packet in enumerate(packets):
            execution = config.executor(kernel_repo_root=config.kernel_repo_root or Path("missing"), bridge_path=config.bridge_path, packet=packet, timeout_seconds=config.timeout_seconds)
            packet_result, pg_diags, kernel_diags = _packet_result(packet, execution, index)
            packet_results.append(packet_result)
            diags.extend(pg_diags)
            upstream.extend(kernel_diags)
        req["kernel_l2_executed"] = bool(packet_results) and all(item["l2_audit_status"] != "not_executed" for item in packet_results)
    elif packets:
        blocked = "invalid" if any(item.severity == "error" for item in diags) else "insufficient_evidence"
        packet_results = [_not_executed(packet, blocked) for packet in packets]

    result = _build_result(bundle, intake, config, diags, upstream, packet_results, req)
    return _finalize(result, config.schema_root)


def _binding_diags(packets: list[Any]) -> list[Diagnostic]:
    out: list[Diagnostic] = []
    packet_ids: set[str] = set()
    decision_ids: set[str] = set()
    for index, packet in enumerate(packets):
        if not isinstance(packet, dict):
            continue
        base = f"$.payload.data.decision_packets[{index}]"
        packet_id, decision_id, family = packet.get("packet_id"), packet.get("decision_id"), packet.get("decision_family_id")
        if packet_id in packet_ids:
            out.append(diagnostic("PG.KERNEL.DUPLICATE_PACKET_ID", "error", "packet_id must be unique.", f"{base}.packet_id"))
        packet_ids.add(packet_id)
        if decision_id in decision_ids:
            out.append(diagnostic("PG.KERNEL.DUPLICATE_DECISION_ID", "error", "decision_id must be unique across packets.", f"{base}.decision_id"))
        decision_ids.add(decision_id)
        record, resolver = packet.get("decision_record", {}), packet.get("resolver_input", {})
        if record.get("decision_id") != decision_id:
            out.append(diagnostic("PG.KERNEL.DECISION_ID_MISMATCH", "error", "Packet and Decision Record decision IDs must match.", f"{base}.decision_record.decision_id"))
        if record.get("decision_family_id") != family or resolver.get("decision_family_id") != family:
            out.append(diagnostic("PG.KERNEL.DECISION_FAMILY_MISMATCH", "error", "Packet, Decision Record, and Resolver input families must match.", f"{base}.decision_family_id"))
        if canonical_sha256(record.get("evidence_refs", [])) != canonical_sha256(resolver.get("evidence_refs", [])):
            out.append(diagnostic("PG.KERNEL.EVIDENCE_REF_MISMATCH", "error", "Decision Record and Resolver input evidence refs must match exactly.", f"{base}.resolver_input.evidence_refs"))
        evidence_ids = [item.get("evidence_id") for item in record.get("evidence_refs", []) if isinstance(item, dict)]
        required = resolver.get("context", {}).get("required_evidence_refs", []) if isinstance(resolver.get("context"), dict) else []
        if any(ref not in evidence_ids for ref in required):
            out.append(diagnostic("PG.KERNEL.REQUIRED_EVIDENCE_REF_BINDING_FAILED", "error", "Resolver-required evidence refs must be present in the packet evidence set.", f"{base}.resolver_input.context.required_evidence_refs"))
        provenance = packet.get("provenance", {})
        if provenance.get("evidence_refs") != evidence_ids:
            out.append(diagnostic("PG.KERNEL.PROVENANCE_EVIDENCE_BINDING_FAILED", "error", "Packet provenance evidence refs must exactly match Decision Record evidence refs.", f"{base}.provenance.evidence_refs"))
        core = {"decision_record": record, "resolver_input": resolver, "audit_context": packet.get("audit_context", {})}
        if provenance.get("content_sha256") != canonical_sha256(core):
            out.append(diagnostic("PG.KERNEL.PROVENANCE_HASH_MISMATCH", "error", "Packet provenance hash does not bind the embedded L2 inputs.", f"{base}.provenance.content_sha256"))
        for claim_index, claim in enumerate(packet.get("asserted_claims", [])):
            if isinstance(claim, dict) and (claim.get("source") != provenance.get("source_repository") or claim.get("provenance_ref") != provenance.get("provenance_id")):
                out.append(diagnostic("PG.KERNEL.CLAIM_PROVENANCE_BINDING_FAILED", "error", "Asserted claim source and provenance must bind to packet provenance.", f"{base}.asserted_claims[{claim_index}]"))
    return sort_diagnostics(out)


def _packet_result(packet: dict[str, Any], execution: KernelAuditExecution, index: int) -> tuple[dict[str, Any], list[Diagnostic], list[dict[str, Any]]]:
    pg: list[Diagnostic] = []
    kernel: list[dict[str, Any]] = []
    if execution.execution_status == "execution_failure":
        pg.append(diagnostic(execution.failure_code or "PG.KERNEL.EXECUTION_FAILED", "insufficient_evidence", "Pinned Kernel L2 execution was unavailable.", f"$.payload.data.decision_packets[{index}]"))
        status, audit, human = "insufficient_evidence", "not_executed", False
    elif execution.execution_status != "executed" or not isinstance(execution.result, dict):
        pg.append(diagnostic(execution.failure_code or "PG.KERNEL.OUTPUT_UNKNOWN", "error", "Kernel bridge returned malformed or unknown structured output.", f"$.payload.data.decision_packets[{index}]"))
        status, audit, human = "invalid", "not_executed", False
    else:
        result = execution.result
        audit = result["audit_status"]
        human = result.get("human_override_observed") is True
        kernel = list(result.get("diagnostics", []))
        resolver_status = result.get("resolver_output", {}).get("resolver_status") if isinstance(result.get("resolver_output"), dict) else None
        codes = {item.get("code") for item in kernel if isinstance(item, dict)}
        if audit == "fail": status = "invalid"
        elif audit == "unsupported" or resolver_status == "unresolvable": status = "insufficient_evidence"
        elif "L2_DECISION_REQUIRES_REAUDIT" in codes: status = "repair_needed"
        else: status = "accepted"
        if human and status == "accepted":
            pg.append(diagnostic("PG.KERNEL.HUMAN_OVERRIDE_OBSERVED", "info", "Explicit human override was observed; it is informational and does not upgrade evidence.", f"$.payload.data.decision_packets[{index}].decision_record.human_override"))
    source_refs, runtime_refs = _split_refs(packet.get("decision_record", {}).get("evidence_refs", []))
    value = {"packet_id":packet.get("packet_id","unknown"),"decision_id":packet.get("decision_id","unknown"),"decision_family_id":packet.get("decision_family_id","unknown"),"status":status,"l2_audit_status":audit,"human_override_observed":human,"diagnostics":[item.to_dict() for item in sort_diagnostics(pg)],"upstream_diagnostics":kernel,"decision_record_ref":packet.get("decision_id","unknown"),"source_evidence_refs":source_refs,"runtime_evidence_refs":runtime_refs,"hashes":{"packet_hash":{"algorithm":"sha256","canonicalization":"ev4-canonical-json.v1","scope":"decision_packet","value":canonical_sha256(packet)},"kernel_stdout_hash":{"algorithm":"sha256","canonicalization":"file_bytes","scope":"kernel_stdout","value":execution.stdout_sha256},"kernel_stderr_hash":{"algorithm":"sha256","canonicalization":"file_bytes","scope":"kernel_stderr","value":execution.stderr_sha256}},"provenance":packet.get("provenance",{})}
    return value, pg, kernel


def _not_executed(packet: dict[str, Any], status: str) -> dict[str, Any]:
    source_refs, runtime_refs = _split_refs(packet.get("decision_record", {}).get("evidence_refs", []))
    return {"packet_id":packet.get("packet_id","unknown"),"decision_id":packet.get("decision_id","unknown"),"decision_family_id":packet.get("decision_family_id","unknown"),"status":status,"l2_audit_status":"not_executed","human_override_observed":False,"diagnostics":[],"upstream_diagnostics":[],"decision_record_ref":packet.get("decision_id","unknown"),"source_evidence_refs":source_refs,"runtime_evidence_refs":runtime_refs,"hashes":{"packet_hash":{"algorithm":"sha256","canonicalization":"ev4-canonical-json.v1","scope":"decision_packet","value":canonical_sha256(packet)}},"provenance":packet.get("provenance",{})}


def _build_result(bundle: Any, intake: dict[str, Any] | None, config: KernelIntakeConfig, diags: list[Diagnostic], upstream: list[dict[str, Any]], packets: list[dict[str, Any]], req: dict[str, bool]) -> dict[str, Any]:
    ordered = sort_diagnostics(diags)
    statuses = [item["status"] for item in packets]
    overall = max(statuses, key=lambda item: _STATUS_RANK[item]) if statuses else _status(ordered)
    if any(item.severity == "error" for item in ordered): overall = "invalid"
    elif any(item.severity == "insufficient_evidence" for item in ordered) and overall != "invalid": overall = "insufficient_evidence"
    source_refs = sorted({ref for item in packets for ref in item["source_evidence_refs"]})
    runtime_refs = sorted({ref for item in packets for ref in item["runtime_evidence_refs"]})
    decisions = (intake or {}).get("decision_packets", [])
    counts = {"provisional_count":sum(1 for item in decisions if item.get("decision_record",{}).get("provisional_status",{}).get("is_provisional") is True),"human_override_count":sum(1 for item in packets if item["human_override_observed"]),"unresolved_decision_count":sum(1 for item in packets if item["status"] in {"repair_needed","insufficient_evidence"}),"accepted_decision_count":sum(1 for item in packets if item["status"] == "accepted"),"rejected_decision_count":sum(1 for item in packets if item["status"] == "invalid")}
    pin = (intake or {}).get("kernel_pin") or {"repository":KERNEL_REPOSITORY,"accepted_commit":KERNEL_COMMIT,"semantic_lock_id":LOCK_ID}
    return {"schema_version":RESULT_SCHEMA_VERSION,"result_type":"kernel_decision_intake","status":overall,"kernel_pin":pin,"accepted_requires":req,"diagnostics":[item.to_dict() for item in ordered],"upstream_diagnostics":upstream,"packet_results":packets,"derived_counts":counts,"decision_record_refs":sorted({item["decision_record_ref"] for item in packets}),"source_evidence_refs":source_refs,"runtime_evidence_refs":runtime_refs,"hashes":{"source_bundle_hash":{"algorithm":"sha256","canonicalization":"ev4-canonical-json.v1","scope":"source_bundle","value":canonical_sha256(bundle)},"semantic_lock_hash":{"algorithm":"sha256","canonicalization":"ev4-canonical-json.v1","scope":"semantic_lock","value":canonical_sha256(config.semantic_lock)}},"provenance":{"source_bundle_provenance":bundle.get("provenance") if isinstance(bundle,dict) else None,"project_gate_derivation":"ev4-project-gate-kroad-011.v1"}}


def _finalize(result: dict[str, Any], schema_root: Path) -> dict[str, Any]:
    schema = load_json_file(schema_root / "kernel-decision-intake-result" / "kernel-decision-intake-result.v1.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(result), key=lambda item: (_json_path(list(item.path)), item.message))
    if not errors:
        return result
    result["accepted_requires"]["result_schema_valid"] = False
    result["status"] = "invalid"
    result["diagnostics"] = [{"code":"PG.KERNEL.RESULT_SCHEMA_INVALID","severity":"error","message":item.message,"path":_json_path(list(item.path))} for item in errors]
    if list(Draft202012Validator(schema).iter_errors(result)):
        raise RuntimeError("Project Gate failed to construct a schema-valid Kernel intake result.")
    return result


def _schema_diags(schema: dict[str, Any], value: Any, code: str, prefix: str = "$") -> list[Diagnostic]:
    out = []
    for item in sorted(Draft202012Validator(schema).iter_errors(value), key=lambda error: (_json_path(list(error.path)), error.message)):
        path = _json_path(list(item.path))
        if prefix != "$": path = prefix + path[1:]
        out.append(diagnostic(code, "error", item.message, path))
    return out


def _find_keys(value: Any, names: set[str], path: str = "$") -> list[tuple[str, str]]:
    out = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in names: out.append((child_path, key))
            out.extend(_find_keys(child, names, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value): out.extend(_find_keys(child, names, f"{path}[{index}]"))
    return out


def _find_claims(value: Any, path: str = "$") -> list[tuple[str, str]]:
    out = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in UNSUPPORTED_ASSERTED_CLAIMS: out.append((child_path, key))
            if key == "claim" and child in UNSUPPORTED_ASSERTED_CLAIMS: out.append((child_path, child))
            out.extend(_find_claims(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if child in UNSUPPORTED_ASSERTED_CLAIMS: out.append((child_path, child))
            out.extend(_find_claims(child, child_path))
    return sorted(set(out))


def _split_refs(refs: Any) -> tuple[list[str], list[str]]:
    source, runtime = [], []
    for item in refs if isinstance(refs, list) else []:
        if not isinstance(item, dict) or not isinstance(item.get("evidence_id"), str): continue
        (runtime if item.get("evidence_tier") in {"runtime_browser","downstream_validated"} else source).append(item["evidence_id"])
    return sorted(set(source)), sorted(set(runtime))


def _status(diags: list[Diagnostic]) -> str:
    if any(item.severity == "error" for item in diags): return "invalid"
    if any(item.severity == "insufficient_evidence" for item in diags): return "insufficient_evidence"
    if any(item.severity == "warning" for item in diags): return "repair_needed"
    return "accepted"


def _json_path(parts: list[Any]) -> str:
    out = "$"
    for part in parts: out += f"[{part}]" if isinstance(part, int) else f".{part}"
    return out
