from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError

KNOWN_RISKS = {"Critical", "High", "Medium", "Low"}
KNOWN_STATUSES = {
    "prose_only",
    "schema_backed",
    "validator_backed",
    "fixture_tested",
    "ci_enforced",
    "downstream_contract_enforced",
}
ENFORCED_STATUSES = KNOWN_STATUSES - {"prose_only"}
TARGETS_REQUIRING_INVALID_FIXTURE = {"fixture_tested", "ci_enforced", "downstream_contract_enforced"}
PROJECT_GATE_REPOSITORY = "rezahh107/EV4-Project-Gate"
PROJECT_GATE_SCHEMA_REGISTRY = {
    "stage-bundle.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/stage-bundle/stage-bundle.v1.schema.json",
        "contract_version": "1.0.0",
    },
    "transition-result.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/transition-result/transition-result.v1.schema.json",
        "contract_version": "1.0.0",
    },
    "architect-to-ce-transition-result.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/architect-to-ce-transition-result/architect-to-ce-transition-result.v1.schema.json",
        "contract_version": "1.0.0",
    },
    "diagnostic.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/diagnostic/diagnostic.v1.schema.json",
        "contract_version": "1.0.0",
    },
    "lock-manifest.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/lock-manifest/lock-manifest.v1.schema.json",
        "contract_version": "1.0.0",
    },
    "behavioral-coverage.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json",
        "contract_version": "1.0.0",
    },
    "validator-evidence.v1": {
        "owner_repository": PROJECT_GATE_REPOSITORY,
        "repository_path": "schemas/validator-evidence/validator-evidence.v1.schema.json",
        "contract_version": "1.0.0",
    },
}
_VALIDATOR_FIXTURE_FAMILIES = {
    "validate_coverage_document": ("tests/fixtures/behavioral_coverage/",),
    "validate_coverage_source": ("tests/fixtures/behavioral_coverage/",),
    "validate_transition_result_semantics": ("tests/fixtures/result_envelope/",),
    "validate_stage_bundle_semantics": ("tests/fixtures/stage_bundle/",),
    "scripts/validate-behavioral-rule-coverage.py": ("tests/fixtures/behavioral_coverage/",),
}


@dataclass(frozen=True)
class CoverageDiagnostic:
    code: str
    severity: str
    message: str
    path: str = "$"
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {"code": self.code, "severity": self.severity, "message": self.message, "path": self.path}
        if self.details:
            payload["details"] = self.details
        return payload


class CoverageSourceError(ValueError):
    """Coverage source is missing or unparseable."""


@dataclass(frozen=True)
class CoverageValidationReport:
    source: str
    status: str
    rule_count: int
    diagnostics: list[CoverageDiagnostic]
    evidence_records: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "behavioral-coverage-report.v1",
            "source": self.source,
            "status": self.status,
            "rule_count": self.rule_count,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
            "evidence_records": self.evidence_records,
        }


def load_coverage_document(source: str | Path) -> dict[str, Any]:
    path = Path(source)
    if not path.exists():
        raise CoverageSourceError(f"Coverage source does not exist: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CoverageSourceError(f"Coverage source could not be read: {path}") from exc
    if path.suffix.lower() == ".json":
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise CoverageSourceError(f"Coverage JSON is unparseable: {exc}") from exc
    marker = "```json behavioral-coverage.v1"
    start = text.find(marker)
    if start < 0:
        raise CoverageSourceError("Coverage markdown does not contain a behavioral-coverage.v1 JSON block.")
    block_start = text.find("\n", start)
    block_end = text.find("```", block_start + 1)
    if block_start < 0 or block_end < 0:
        raise CoverageSourceError("Coverage markdown JSON block is malformed.")
    try:
        return json.loads(text[block_start + 1 : block_end])
    except json.JSONDecodeError as exc:
        raise CoverageSourceError(f"Coverage markdown JSON block is unparseable: {exc}") from exc


def inspect_coverage_source(source: str | Path, schema_path: str | Path = "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json") -> CoverageValidationReport:
    return validate_coverage_source(source, schema_path)


def validate_coverage_source(source: str | Path, schema_path: str | Path = "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json") -> CoverageValidationReport:
    source_path = Path(source)
    repo_root = _infer_repo_root(source_path)
    return validate_coverage_document(load_coverage_document(source_path), str(source), schema_path, repo_root=repo_root)


def validate_coverage_document(
    document: dict[str, Any],
    source: str = "<memory>",
    schema_path: str | Path = "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json",
    *,
    repo_root: str | Path | None = None,
) -> CoverageValidationReport:
    root = Path(repo_root) if repo_root is not None else Path.cwd()
    schema_candidate = Path(schema_path)
    schema_file = schema_candidate if schema_candidate.is_absolute() else _resolve_reference_path(root, str(schema_path))
    if schema_file is None or not schema_file.exists():
        raise CoverageSourceError(f"Behavioral coverage schema does not exist: {schema_path}")
    try:
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except OSError as exc:
        raise CoverageSourceError(f"Behavioral coverage schema could not be read: {schema_path}") from exc
    except json.JSONDecodeError as exc:
        raise CoverageSourceError(f"Behavioral coverage schema is unparseable: {exc}") from exc
    except SchemaError as exc:
        raise CoverageSourceError(f"Behavioral coverage schema is invalid: {exc.message}") from exc
    validator = Draft202012Validator(schema)
    diagnostics = [
        CoverageDiagnostic("PG_BRC_SCHEMA_INVALID", "error", error.message, _json_path(error.absolute_path))
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]
    rules = document.get("rules") if isinstance(document, dict) else None
    if not isinstance(rules, list):
        return CoverageValidationReport(source, "thresholds_failed", 0, diagnostics)
    rule_diagnostics, evidence_records = _validate_rules(rules, root)
    diagnostics.extend(rule_diagnostics)
    return CoverageValidationReport(source, "thresholds_met" if not diagnostics else "thresholds_failed", len(rules), diagnostics, evidence_records)


def _validate_rules(rules: list[Any], repo_root: Path) -> tuple[list[CoverageDiagnostic], list[dict[str, Any]]]:
    diagnostics: list[CoverageDiagnostic] = []
    evidence_records: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    for index, rule in enumerate(rules):
        path = f"$.rules[{index}]"
        if not isinstance(rule, dict):
            diagnostics.append(CoverageDiagnostic("PG_BRC_RULE_NOT_OBJECT", "error", "Coverage rule must be an object.", path))
            continue
        rule_id = rule.get("rule_id")
        risk = rule.get("risk")
        status = rule.get("status")
        target_status = rule.get("target_status", status)
        carriers = _list(rule.get("carriers"))
        validators = _list(rule.get("validators"))
        valid_fixtures = _list(rule.get("valid_fixtures"))
        invalid_fixtures = _list(rule.get("invalid_fixtures"))
        ci_steps = _list(rule.get("ci_steps"))
        downstream_contracts = _list(rule.get("downstream_contracts"))
        downstream_rejection_fixtures = _list(rule.get("downstream_rejection_fixtures"))
        if not isinstance(rule_id, str) or not _stable_rule_id(rule_id):
            diagnostics.append(CoverageDiagnostic("PG_BRC_RULE_ID_MUST_BE_STABLE", "error", "rule_id must match PG-<AREA>-NNN.", f"{path}.rule_id"))
        elif rule_id in seen:
            diagnostics.append(CoverageDiagnostic("PG_BRC_RULE_ID_MUST_NOT_BE_REUSED", "error", "rule_id appears more than once.", f"{path}.rule_id", {"first_index": seen[rule_id], "duplicate_index": index}))
        else:
            seen[rule_id] = index
        if risk not in KNOWN_RISKS:
            diagnostics.append(CoverageDiagnostic("PG_BRC_RISK_MUST_BE_KNOWN", "error", "risk must be Critical, High, Medium, or Low.", f"{path}.risk"))
        if status not in KNOWN_STATUSES:
            diagnostics.append(CoverageDiagnostic("PG_BRC_STATUS_MUST_BE_KNOWN", "error", "status is not known.", f"{path}.status"))
            continue
        if risk == "Critical" and status == "prose_only":
            diagnostics.append(CoverageDiagnostic("PG_BRC_CRITICAL_MUST_NOT_BE_PROSE_ONLY", "error", "Critical rules must not remain prose_only.", f"{path}.status"))
        if risk == "Critical" and status == "schema_backed" and not rule.get("next_enforcement_step"):
            diagnostics.append(CoverageDiagnostic("PG_BRC_CRITICAL_SCHEMA_BACKED_REQUIRES_FOLLOWUP", "error", "Critical schema_backed rules require explicit follow-up.", f"{path}.next_enforcement_step"))
        if risk == "High" and status == "prose_only" and not rule.get("documented_risk"):
            diagnostics.append(CoverageDiagnostic("PG_BRC_HIGH_PROSE_ONLY_REQUIRES_DOCUMENTED_RISK", "error", "High prose_only rules require documented_risk.", f"{path}.documented_risk"))
        if risk == "Critical" and target_status in TARGETS_REQUIRING_INVALID_FIXTURE and not invalid_fixtures:
            diagnostics.append(CoverageDiagnostic("PG_BRC_INVALID_FIXTURE_REQUIRED_FOR_CRITICAL_TARGET", "error", "Critical target enforcement requires invalid fixtures.", f"{path}.invalid_fixtures"))
        if status == "ci_enforced" and not ci_steps:
            diagnostics.append(CoverageDiagnostic("PG_BRC_CI_STEP_REQUIRED_BEFORE_CI_ENFORCED", "error", "ci_enforced requires at least one CI step.", f"{path}.ci_steps"))
        if status == "downstream_contract_enforced" and not downstream_contracts:
            diagnostics.append(CoverageDiagnostic("PG_BRC_DOWNSTREAM_CONTRACT_REQUIRED_BEFORE_DOWNSTREAM_ENFORCED", "error", "downstream_contract_enforced requires downstream_contracts.", f"{path}.downstream_contracts"))
        if status in ENFORCED_STATUSES and not carriers:
            diagnostics.append(CoverageDiagnostic("PG_BRC_NO_CLAIMED_ENFORCEMENT_WITHOUT_CARRIER", "error", "Claimed enforcement requires a carrier.", f"{path}.carriers"))
        if status in {"validator_backed", "fixture_tested", "ci_enforced", "downstream_contract_enforced"} and not validators:
            diagnostics.append(CoverageDiagnostic("PG_BRC_NO_CLAIMED_ENFORCEMENT_WITHOUT_VALIDATOR", "error", "Validator-backed or stronger status requires validators.", f"{path}.validators"))
        if status in {"fixture_tested", "ci_enforced", "downstream_contract_enforced"} and not (valid_fixtures or invalid_fixtures):
            diagnostics.append(CoverageDiagnostic("PG_BRC_NO_CLAIMED_ENFORCEMENT_WITHOUT_FIXTURE", "error", "Fixture-tested or stronger status requires fixtures.", f"{path}.valid_fixtures"))
        if status == "downstream_contract_enforced" and not downstream_rejection_fixtures:
            diagnostics.append(CoverageDiagnostic("PG_BRC_NO_CLAIMED_DOWNSTREAM_ENFORCEMENT_WITHOUT_REJECTION_FIXTURE", "error", "Downstream enforcement requires a rejection fixture.", f"{path}.downstream_rejection_fixtures"))
        if status in ENFORCED_STATUSES:
            for offset, ref in enumerate(carriers):
                diagnostics.extend(_resolve_existing_file(repo_root, ref, f"{path}.carriers[{offset}]", "PG_BRC_CARRIER_REFERENCE_INVALID", evidence_records, "carrier"))
        if status in {"validator_backed", "fixture_tested", "ci_enforced", "downstream_contract_enforced"}:
            validator_bindings: list[str] = []
            for offset, ref in enumerate(validators):
                validator_bindings.extend(_resolve_validator_reference(repo_root, ref, f"{path}.validators[{offset}]", diagnostics, evidence_records))
            if status in {"fixture_tested", "ci_enforced", "downstream_contract_enforced"}:
                for field_name, refs in (("valid_fixtures", valid_fixtures), ("invalid_fixtures", invalid_fixtures)):
                    for offset, ref in enumerate(refs):
                        diagnostics.extend(_resolve_existing_file(repo_root, ref, f"{path}.{field_name}[{offset}]", "PG_BRC_FIXTURE_REFERENCE_INVALID", evidence_records, "fixture"))
                        if validator_bindings and not _fixture_bound_to_validator(ref, validator_bindings):
                            diagnostics.append(CoverageDiagnostic("PG_BRC_FIXTURE_NOT_BOUND_TO_VALIDATOR", "error", "Fixture path is not bound to any declared validator family.", f"{path}.{field_name}[{offset}]", {"fixture": ref, "validators": validator_bindings}))
        for offset, ref in enumerate(ci_steps):
            diagnostics.extend(_resolve_ci_step(repo_root, ref, f"{path}.ci_steps[{offset}]", evidence_records))
        if status == "downstream_contract_enforced":
            for offset, ref in enumerate(downstream_contracts):
                diagnostics.extend(_resolve_existing_file(repo_root, ref, f"{path}.downstream_contracts[{offset}]", "PG_BRC_DOWNSTREAM_CONTRACT_REFERENCE_INVALID", evidence_records, "downstream_contract"))
            for offset, ref in enumerate(downstream_rejection_fixtures):
                diagnostics.extend(_resolve_existing_file(repo_root, ref, f"{path}.downstream_rejection_fixtures[{offset}]", "PG_BRC_DOWNSTREAM_REJECTION_FIXTURE_REFERENCE_INVALID", evidence_records, "downstream_rejection_fixture"))
    return diagnostics, evidence_records


def validate_transition_result_semantics(payload: dict[str, Any]) -> list[CoverageDiagnostic]:
    diagnostics: list[CoverageDiagnostic] = []
    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    source_provenance = provenance.get("source_provenance") if isinstance(provenance.get("source_provenance"), dict) else {}
    produced_by = provenance.get("produced_by") if isinstance(provenance.get("produced_by"), dict) else {}
    if payload.get("status") == "accepted":
        official_validators = produced_by.get("official_validators")
        if not isinstance(official_validators, list) or not official_validators:
            diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_ACCEPTED_MISSING_VALIDATOR_EVIDENCE", "error", "accepted result requires explicit official validator evidence.", "$.provenance.produced_by.official_validators"))
        else:
            for index, validator_record in enumerate(official_validators):
                diagnostics.extend(_validate_validator_evidence_record(payload, validator_record, index))
        if source_provenance.get("synthetic") is True or source_provenance.get("verification_state") == "synthetic_fixture_only" or source_provenance.get("kind") == "synthetic_fixture":
            diagnostics.append(CoverageDiagnostic("PG_SYNTH_SYNTHETIC_ONLY_MARKED_ACCEPTED", "error", "synthetic-only evidence must not be marked accepted as real EV4 evidence.", "$.provenance.source_provenance"))
    output_write = produced_by.get("output_write")
    if payload.get("status") in {"accepted", "valid"} and isinstance(output_write, dict) and output_write.get("attempted") is True and output_write.get("succeeded") is False:
        diagnostics.append(CoverageDiagnostic("PG_OUTPUT_WRITE_FAILED_BUT_SUCCESS_STATUS", "error", "A successful status must not be emitted when output writing failed.", "$.provenance.produced_by.output_write.succeeded"))
    return diagnostics


def validate_stage_bundle_semantics(payload: dict[str, Any], repo_root: str | Path | None = None) -> list[CoverageDiagnostic]:
    diagnostics: list[CoverageDiagnostic] = []
    payload_schema = payload.get("payload_schema") if isinstance(payload.get("payload_schema"), dict) else {}
    schema_id = payload_schema.get("id")
    owner_repository = payload_schema.get("owner_repository")
    if owner_repository == PROJECT_GATE_REPOSITORY:
        entry = PROJECT_GATE_SCHEMA_REGISTRY.get(schema_id)
        if entry is None:
            return [CoverageDiagnostic("PG_BOUNDARY_COPIED_SPECIALIST_SCHEMA_CLAIMED_AS_PROJECT_GATE_OWNED", "error", "Project Gate-owned schema claims must match the exact Project Gate schema registry.", "$.payload_schema", {"schema_id": schema_id, "owner_repository": owner_repository})]
        root = Path(repo_root) if repo_root is not None else Path.cwd()
        schema_file = _resolve_reference_path(root, entry["repository_path"])
        if schema_file is None or not schema_file.is_file():
            diagnostics.append(CoverageDiagnostic("PG_SCHEMA_REGISTRY_PATH_MISSING", "error", "Registered Project Gate schema path does not exist.", "$.payload_schema", {"schema_id": schema_id, "repository_path": entry["repository_path"]}))
    return diagnostics


def _validate_validator_evidence_record(payload: dict[str, Any], record: Any, index: int) -> list[CoverageDiagnostic]:
    path = f"$.provenance.produced_by.official_validators[{index}]"
    diagnostics: list[CoverageDiagnostic] = []
    if not isinstance(record, dict):
        return [CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_EVIDENCE_MALFORMED", "error", "official validator evidence entry must be an object.", path)]
    required = (
        "schema_version",
        "validator_id",
        "owner_repository",
        "validator_path",
        "execution_id",
        "status",
        "validated_stage",
        "validated_scope",
        "validated_hash",
        "result_digest",
    )
    missing = [field for field in required if field not in record]
    if missing:
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_EVIDENCE_MALFORMED", "error", "official validator evidence entry is missing required fields.", path, {"missing": missing}))
    if record.get("schema_version") != "validator-evidence.v1":
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_EVIDENCE_MALFORMED", "error", "validator evidence schema_version must be validator-evidence.v1.", f"{path}.schema_version"))
    if record.get("status") != "passed":
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_STATUS_NOT_PASSED", "error", "accepted result requires validator evidence status=passed.", f"{path}.status", {"status": record.get("status")}))
    if not record.get("accepted_commit") and not record.get("validator_file_hash"):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_UNPINNED", "error", "validator evidence requires accepted_commit or validator_file_hash.", path))
    if record.get("accepted_commit") is not None and not _is_sha1(record.get("accepted_commit")):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_UNPINNED", "error", "accepted_commit must be a 40-character lowercase SHA-1.", f"{path}.accepted_commit"))
    if record.get("validator_file_hash") is not None and not _is_sha256(record.get("validator_file_hash")):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_UNPINNED", "error", "validator_file_hash must be a 64-character lowercase SHA-256.", f"{path}.validator_file_hash"))
    if record.get("validated_stage") != payload.get("source_stage"):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_STAGE_MISMATCH", "error", "validator evidence stage must match source_stage.", f"{path}.validated_stage", {"expected": payload.get("source_stage"), "actual": record.get("validated_stage")}))
    expected_hash = None
    scope = record.get("validated_scope")
    if scope == "payload":
        expected_hash = ((payload.get("hashes") or {}).get("canonical_payload_hash") or {}).get("value")
    elif scope == "source_bundle":
        expected_hash = ((payload.get("hashes") or {}).get("source_bundle_hash") or {}).get("value")
    else:
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_SCOPE_MISMATCH", "error", "validated_scope must be payload or source_bundle.", f"{path}.validated_scope", {"actual": scope}))
    if expected_hash is not None and record.get("validated_hash") != expected_hash:
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_HASH_MISMATCH", "error", "validator evidence validated_hash must match the declared result hash for its scope.", f"{path}.validated_hash", {"expected": expected_hash, "actual": record.get("validated_hash")}))
    if not _is_sha256(record.get("result_digest")):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_RESULT_DIGEST_INVALID", "error", "validator evidence result_digest must be a lowercase SHA-256.", f"{path}.result_digest"))
    if not isinstance(record.get("validator_path"), str) or not record.get("validator_path"):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_EVIDENCE_MALFORMED", "error", "validator_path must be a non-empty string.", f"{path}.validator_path"))
    if not isinstance(record.get("owner_repository"), str) or not re.match(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", record.get("owner_repository", "")):
        diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_VALIDATOR_EVIDENCE_MALFORMED", "error", "owner_repository must be owner/repo.", f"{path}.owner_repository"))
    return diagnostics


def _resolve_existing_file(repo_root: Path, ref: Any, path: str, code: str, evidence_records: list[dict[str, Any]], kind: str) -> list[CoverageDiagnostic]:
    if not isinstance(ref, str):
        return [CoverageDiagnostic(code, "error", "Reference must be a repository-relative path string.", path)]
    resolved = _resolve_reference_path(repo_root, ref)
    if resolved is None:
        return [CoverageDiagnostic(code, "error", "Reference must stay inside the repository and must not be absolute or external.", path, {"reference": ref})]
    if not resolved.is_file():
        return [CoverageDiagnostic(code, "error", "Referenced evidence file does not exist.", path, {"reference": ref})]
    evidence_records.append(_file_evidence_record(kind, repo_root, resolved))
    return []


def _resolve_validator_reference(repo_root: Path, ref: Any, path: str, diagnostics: list[CoverageDiagnostic], evidence_records: list[dict[str, Any]]) -> list[str]:
    bindings: list[str] = []
    if not isinstance(ref, str):
        diagnostics.append(CoverageDiagnostic("PG_BRC_VALIDATOR_REFERENCE_INVALID", "error", "Validator reference must be a string.", path))
        return bindings
    if ":" in ref and "::" not in ref:
        diagnostics.append(CoverageDiagnostic("PG_BRC_VALIDATOR_REFERENCE_INVALID", "error", "Validator references must use repository path or path::symbol, not unresolved module strings.", path, {"reference": ref}))
        return bindings
    file_part, symbol = (ref.split("::", 1) + [None])[:2] if "::" in ref else (ref, None)
    if file_part.startswith("script:"):
        file_part = file_part.removeprefix("script:")
    resolved = _resolve_reference_path(repo_root, file_part)
    if resolved is None or not resolved.is_file():
        diagnostics.append(CoverageDiagnostic("PG_BRC_VALIDATOR_REFERENCE_INVALID", "error", "Validator file does not exist.", path, {"reference": ref}))
        return bindings
    evidence_records.append(_file_evidence_record("validator", repo_root, resolved, {"symbol": symbol} if symbol else None))
    if symbol:
        text = resolved.read_text(encoding="utf-8")
        if not re.search(rf"^\s*def\s+{re.escape(symbol)}\s*\(", text, re.MULTILINE):
            diagnostics.append(CoverageDiagnostic("PG_BRC_VALIDATOR_SYMBOL_NOT_FOUND", "error", "Declared validator symbol was not found in the validator file.", path, {"reference": ref, "symbol": symbol}))
            return bindings
        bindings.append(symbol)
    else:
        bindings.append(_relative_posix(repo_root, resolved))
    return bindings


def _resolve_ci_step(repo_root: Path, ref: Any, path: str, evidence_records: list[dict[str, Any]]) -> list[CoverageDiagnostic]:
    if not isinstance(ref, str):
        return [CoverageDiagnostic("PG_BRC_CI_STEP_REFERENCE_INVALID", "error", "CI step reference must be a string.", path)]
    parts = [part.strip() for part in ref.split(" / ")]
    if len(parts) not in {2, 3}:
        return [CoverageDiagnostic("PG_BRC_CI_STEP_REFERENCE_INVALID", "error", "CI step reference must use '<workflow.yml> / <step name>' or '<workflow.yml> / <job id> / <step name>'.", path, {"reference": ref})]
    workflow_ref = parts[0]
    job_id = parts[1] if len(parts) == 3 else None
    step_name = parts[-1]
    workflow_path = _resolve_reference_path(repo_root, workflow_ref)
    if workflow_path is None or not workflow_path.is_file():
        return [CoverageDiagnostic("PG_BRC_CI_STEP_REFERENCE_INVALID", "error", "Referenced workflow file does not exist.", path, {"reference": ref})]
    text = workflow_path.read_text(encoding="utf-8")
    diagnostics: list[CoverageDiagnostic] = []
    if job_id and not re.search(rf"^\s{{2}}{re.escape(job_id)}:\s*$", text, re.MULTILINE):
        diagnostics.append(CoverageDiagnostic("PG_BRC_CI_JOB_REFERENCE_INVALID", "error", "Referenced CI job id does not exist in workflow.", path, {"reference": ref, "job_id": job_id}))
    if not re.search(rf"^\s*-\s+name:\s+['\"]?{re.escape(step_name)}['\"]?\s*$", text, re.MULTILINE):
        diagnostics.append(CoverageDiagnostic("PG_BRC_CI_STEP_REFERENCE_INVALID", "error", "Referenced CI step name does not exist in workflow.", path, {"reference": ref, "step_name": step_name}))
    if not diagnostics:
        evidence_records.append(_file_evidence_record("ci_step", repo_root, workflow_path, {"step_name": step_name, "job_id": job_id}))
    return diagnostics


def _fixture_bound_to_validator(ref: str, validator_bindings: list[str]) -> bool:
    normalized = ref.replace("\\", "/")
    allowed_families: list[str] = []
    for binding in validator_bindings:
        allowed_families.extend(_VALIDATOR_FIXTURE_FAMILIES.get(binding, ()))
    return any(normalized.startswith(family) for family in allowed_families)


def _resolve_reference_path(repo_root: Path, reference: str) -> Path | None:
    if reference.startswith(("http://", "https://", "git://")):
        return None
    candidate = Path(reference)
    if candidate.is_absolute():
        return None
    try:
        resolved = (repo_root / candidate).resolve()
        root = repo_root.resolve()
    except OSError:
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def _infer_repo_root(source_path: Path) -> Path:
    path = source_path if source_path.is_dir() else source_path.parent
    for candidate in (path, *path.parents):
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    return Path.cwd()


def _file_evidence_record(kind: str, repo_root: Path, path: Path, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "kind": kind,
        "path": _relative_posix(repo_root, path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    if extra:
        payload.update(extra)
    return payload


def _relative_posix(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _stable_rule_id(value: str) -> bool:
    parts = value.split("-")
    return len(parts) >= 3 and parts[0] == "PG" and parts[-1].isdigit() and len(parts[-1]) == 3 and all(parts[1:-1])


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _json_path(path: Iterable[Any]) -> str:
    rendered = "$"
    for part in path:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _is_sha1(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{40}", value) is not None


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None
