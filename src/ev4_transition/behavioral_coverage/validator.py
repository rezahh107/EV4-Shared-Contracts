from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

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
PROJECT_GATE_SCHEMA_PREFIXES = (
    "stage-bundle",
    "transition-result",
    "architect-to-ce-transition-result",
    "diagnostic",
    "lock-manifest",
    "behavioral-coverage",
)


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "behavioral-coverage-report.v1",
            "source": self.source,
            "status": self.status,
            "rule_count": self.rule_count,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
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
    return validate_coverage_document(load_coverage_document(source), str(source), schema_path)


def validate_coverage_document(document: dict[str, Any], source: str = "<memory>", schema_path: str | Path = "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json") -> CoverageValidationReport:
    schema_file = Path(schema_path)
    if not schema_file.exists():
        raise CoverageSourceError(f"Behavioral coverage schema does not exist: {schema_file}")
    try:
        schema = json.loads(schema_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CoverageSourceError(f"Behavioral coverage schema is unparseable: {exc}") from exc
    validator = Draft202012Validator(schema)
    diagnostics = [
        CoverageDiagnostic("PG_BRC_SCHEMA_INVALID", "error", error.message, _json_path(error.absolute_path))
        for error in sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    ]
    rules = document.get("rules") if isinstance(document, dict) else None
    if not isinstance(rules, list):
        return CoverageValidationReport(source, "thresholds_failed", 0, diagnostics)
    diagnostics.extend(_validate_rules(rules))
    return CoverageValidationReport(source, "thresholds_met" if not diagnostics else "thresholds_failed", len(rules), diagnostics)


def _validate_rules(rules: list[Any]) -> list[CoverageDiagnostic]:
    diagnostics: list[CoverageDiagnostic] = []
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
    return diagnostics


def validate_transition_result_semantics(payload: dict[str, Any]) -> list[CoverageDiagnostic]:
    diagnostics: list[CoverageDiagnostic] = []
    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    source_provenance = provenance.get("source_provenance") if isinstance(provenance.get("source_provenance"), dict) else {}
    produced_by = provenance.get("produced_by") if isinstance(provenance.get("produced_by"), dict) else {}
    if payload.get("status") == "accepted":
        official_validators = produced_by.get("official_validators")
        if not isinstance(official_validators, list) or not official_validators:
            diagnostics.append(CoverageDiagnostic("PG_EVIDENCE_ACCEPTED_MISSING_VALIDATOR_EVIDENCE", "error", "accepted result requires explicit official validator evidence.", "$.provenance.produced_by.official_validators"))
        if source_provenance.get("synthetic") is True or source_provenance.get("verification_state") == "synthetic_fixture_only" or source_provenance.get("kind") == "synthetic_fixture":
            diagnostics.append(CoverageDiagnostic("PG_SYNTH_SYNTHETIC_ONLY_MARKED_ACCEPTED", "error", "synthetic-only evidence must not be marked accepted as real EV4 evidence.", "$.provenance.source_provenance"))
    output_write = produced_by.get("output_write")
    if payload.get("status") in {"accepted", "valid"} and isinstance(output_write, dict) and output_write.get("attempted") is True and output_write.get("succeeded") is False:
        diagnostics.append(CoverageDiagnostic("PG_OUTPUT_WRITE_FAILED_BUT_SUCCESS_STATUS", "error", "A successful status must not be emitted when output writing failed.", "$.provenance.produced_by.output_write.succeeded"))
    return diagnostics


def validate_stage_bundle_semantics(payload: dict[str, Any]) -> list[CoverageDiagnostic]:
    payload_schema = payload.get("payload_schema") if isinstance(payload.get("payload_schema"), dict) else {}
    schema_id = payload_schema.get("id")
    owner_repository = payload_schema.get("owner_repository")
    if owner_repository == PROJECT_GATE_REPOSITORY and isinstance(schema_id, str) and not schema_id.startswith(PROJECT_GATE_SCHEMA_PREFIXES):
        return [CoverageDiagnostic("PG_BOUNDARY_COPIED_SPECIALIST_SCHEMA_CLAIMED_AS_PROJECT_GATE_OWNED", "error", "Project Gate must not claim specialist schemas as Project Gate-owned contracts.", "$.payload_schema", {"schema_id": schema_id, "owner_repository": owner_repository})]
    return []


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
